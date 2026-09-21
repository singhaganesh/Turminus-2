"""Map-before-link symmap contract verifier."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

RUNTIME = Path("/app/symmill/fold/runtime")
SYMAP = Path("/app/symmill/fold/runtime.symmap")
PROFILE = Path("/app/symmill/fold/profile.json")
BENCH = Path("/app/benchframes/bench.samples")
PCFOLD = Path("/opt/verifier/bin/pcfold-grade")
AGENT_PCFOLD = Path("/app/bin/pcfold")
_HEX_RADIX = 16


def _parse_symmap() -> tuple[set[str], dict[str, int], dict[str, int], dict[str, object]]:
    lines = SYMAP.read_text().splitlines()
    assert lines and lines[0].strip() == "PCFOLD1"
    sym_names: set[str] = set()
    addr_by_name: dict[str, int] = {}
    span_by_name: dict[str, int] = {}
    meta: dict[str, object] = {}
    for line in lines[1:]:
        if line.startswith("mode "):
            meta["mode"] = line.split()[1]
        elif line.startswith("buildid "):
            meta["buildid"] = line.split()[1]
        elif line.startswith("sym "):
            parts = line.split()
            name = parts[1]
            sym_names.add(name)
            addr_by_name[name] = int(parts[2], _HEX_RADIX)
            span_by_name[name] = int(parts[3], _HEX_RADIX)
    return sym_names, addr_by_name, span_by_name, meta


def _sym_start(name: str) -> int:
    _, addr_by_name, _, _ = _parse_symmap()
    assert name in addr_by_name, f"{name} missing from symmap"
    return int(addr_by_name[name])


def _live_readelf_build_id() -> str:
    proc = subprocess.run(
        ["readelf", "-n", str(RUNTIME)],
        check=True,
        capture_output=True,
        text=True,
    )
    for line in proc.stdout.splitlines():
        if "Build ID:" in line:
            return line.split("Build ID:")[1].strip()
    raise AssertionError("runtime ELF build id missing")


def _anchor_symbol(name: str) -> int:
    for line in Path("/app/benchframes/anchor/symbols.tab").read_text().splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        if parts[0] == name:
            return int(parts[1], _HEX_RADIX)
    raise AssertionError(f"{name} missing from anchor symbols.tab")


def _nm_text_symbols() -> set[str]:
    proc = subprocess.run(
        ["nm", "-n", "--defined-only", str(RUNTIME)],
        check=True,
        capture_output=True,
        text=True,
    )
    names: set[str] = set()
    for line in proc.stdout.splitlines():
        parts = line.split()
        if len(parts) < 3:
            continue
        if parts[1] in {"T", "t"}:
            names.add(parts[2])
    return names


def _nm_symbol_sizes() -> dict[str, int]:
    proc = subprocess.run(
        ["nm", "-n", "--defined-only", str(RUNTIME)],
        check=True,
        capture_output=True,
        text=True,
    )
    ordered: list[tuple[str, int]] = []
    for line in proc.stdout.splitlines():
        parts = line.split()
        if len(parts) < 3 or parts[1] not in {"T", "t"}:
            continue
        ordered.append((parts[2], int(parts[0], _HEX_RADIX)))
    sizes: dict[str, int] = {}
    for idx, (name, start) in enumerate(ordered):
        if idx + 1 < len(ordered):
            end = ordered[idx + 1][1]
            sizes[name] = max(end - start, 1)
        else:
            sizes[name] = 64
    return sizes


def _render(samples_text: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        sample_path = Path(tmp) / "held_out.samples"
        out_path = Path(tmp) / "held_out.profile.json"
        sample_path.write_text(samples_text)
        subprocess.run(
            [str(PCFOLD), "render", str(sample_path), str(SYMAP), "-o", str(out_path)],
            check=True,
        )
        return json.loads(out_path.read_text())


def test_premap01_symmap_covers_runtime():
    """Symmap must list every exported bench function plus core runtime entry symbols."""
    sym_names, _, _, _ = _parse_symmap()
    required = {"ring_dispatch", "legacy_worker", "main", "_start"}
    assert required <= sym_names
    assert _nm_text_symbols() <= sym_names


def test_premap02_symmap_mode_linked():
    """Symmap mode line must be linked, not an object-merge map."""
    _, _, _, meta = _parse_symmap()
    mode = meta.get("mode")
    assert mode == "linked"


def test_premap03_buildid_present():
    """Symmap buildid must be present and not the object-merge placeholder."""
    _, _, _, meta = _parse_symmap()
    bid = meta.get("buildid")
    assert isinstance(bid, str)
    assert bid not in {"", "object-merge", "unknown"}
    assert len(bid) >= 8  # contract: buildid length >= 8


def test_premap04_buildid_matches_readelf():
    """Symmap buildid must match the linked runtime ELF build id."""
    _, _, _, meta = _parse_symmap()
    assert meta.get("buildid") == _live_readelf_build_id()


def test_premap05_bench_ring_dispatch_name():
    """First bench sample PC must resolve to ring_dispatch by name."""
    profile = json.loads(PROFILE.read_text())
    ring_pc = _sym_start("ring_dispatch") + 8
    match = [s for s in profile["frames"] if int(s["pc"], 16) == ring_pc]
    assert match and match[0]["symbol"] == "ring_dispatch"


def test_premap06_bench_legacy_worker_name():
    """Second bench sample PC must resolve to legacy_worker by name."""
    profile = json.loads(PROFILE.read_text())
    legacy_pc = _sym_start("legacy_worker") + 4
    match = [s for s in profile["frames"] if int(s["pc"], 16) == legacy_pc]
    assert match and match[0]["symbol"] == "legacy_worker"


def test_premap07_held_out_ring_render():
    """Held-out render on linked ring_dispatch PC must resolve to ring_dispatch."""
    ring_pc = _anchor_symbol("ring_dispatch") + 4
    prof = _render(f"pc 0x{ring_pc:x}\n")
    assert prof["frames"][0]["symbol"] == "ring_dispatch"
    assert prof["frames"][0]["symbol"] != "legacy_worker"


def test_premap08_held_out_offset_not_neighbor():
    """Held-out ring_dispatch sample offset must match linked runtime layout."""
    ring_start = _anchor_symbol("ring_dispatch")
    ring_pc = ring_start + 4
    prof = _render(f"pc 0x{ring_pc:x}\n")
    assert prof["frames"][0]["symbol"] == "ring_dispatch"
    assert int(prof["frames"][0]["offset"]) == 4


def test_premap09_profile_json_shape_and_names():
    """profile.json must expose frames with correct ring_dispatch and legacy_worker names."""
    profile = json.loads(PROFILE.read_text())
    assert isinstance(profile["frames"], list)
    ring_pc = _sym_start("ring_dispatch") + 8
    legacy_pc = _sym_start("legacy_worker") + 4
    by_pc = {int(s["pc"], 16): s for s in profile["frames"]}
    assert by_pc[ring_pc]["symbol"] == "ring_dispatch"
    assert by_pc[legacy_pc]["symbol"] == "legacy_worker"
    for row in profile["frames"]:
        assert set(row) >= {"pc", "symbol", "offset"}
        assert isinstance(row["symbol"], str)
        assert isinstance(row["offset"], int)


def test_premap10_ring_dispatch_linked_address():
    """Symmap ring_dispatch entry must use the linked runtime address."""
    linked = _sym_start("ring_dispatch")
    assert linked == _anchor_symbol("ring_dispatch")


def test_premap11_bench_samples_file_used():
    """profile.json must include every bench.samples PC line with matching symbols."""
    pcs = []
    for line in BENCH.read_text().splitlines():
        if line.startswith("pc "):
            pcs.append(int(line.split()[1], 16))
    profile = json.loads(PROFILE.read_text())
    got = {int(s["pc"], 16): s["symbol"] for s in profile["frames"]}
    assert set(pcs) <= set(got)
    for pc in pcs:
        sym = got[pc]
        assert sym in {"ring_dispatch", "legacy_worker"}
        assert sym == (
            "ring_dispatch" if pc == _sym_start("ring_dispatch") + 8 else "legacy_worker"
        )


def test_premap12_pcfold_rejects_tampered_symmap():
    """Agent pcfold check must reject a symmap whose buildid drifts from runtime."""
    live_bid = _live_readelf_build_id()
    drifted = (live_bid[:-1] + ("0" if live_bid[-1] != "0" else "1"))
    tampered_lines = []
    for line in SYMAP.read_text().splitlines():
        if line.startswith("buildid "):
            tampered_lines.append(f"buildid {drifted}")
        else:
            tampered_lines.append(line)
    with tempfile.NamedTemporaryFile("w", suffix=".symmap", delete=False) as tmp:
        tmp.write("\n".join(tampered_lines) + "\n")
        bad_path = tmp.name
    proc = subprocess.run(
        [str(AGENT_PCFOLD), "check", str(RUNTIME), bad_path],
        check=False,
    )
    Path(bad_path).unlink(missing_ok=True)
    assert proc.returncode != 0


def test_premap13_pcfold_check_on_disk_pair():
    """On-disk runtime.symmap must pass agent pcfold check against runtime."""
    _, _, _, meta = _parse_symmap()
    assert meta.get("mode") == "linked"
    proc = subprocess.run(
        [str(AGENT_PCFOLD), "check", str(RUNTIME), str(SYMAP)],
        check=False,
    )
    assert proc.returncode == 0


def test_premap14_symmap_min_rows():
    """Symmap must contain at least eight sym rows per contract."""
    sym_names, _, _, _ = _parse_symmap()
    assert len(sym_names) >= 8


def test_premap15_no_object_index_placeholder_sizes():
    """Linked symmap must not keep object-index 0x40 placeholder spans."""
    _, _, span_by_name, _ = _parse_symmap()
    sizes = list(span_by_name.values())
    assert sizes
    varied_spans = {size for size in sizes if size != 0x40}
    assert varied_spans


def test_premap16_symmap_sizes_match_runtime_nm():
    """Sym row spans must match nm-derived sizes on the linked runtime ELF."""
    _, _, span_by_name, _ = _parse_symmap()
    expected = _nm_symbol_sizes()
    for name, span in span_by_name.items():
        assert name in expected
        assert span == expected[name]


def test_premap18_emitmap_rejects_object_map():
    """emitmap must fail when the on-disk symmap is not a linked identity map."""
    original = SYMAP.read_text()
    profile_original = PROFILE.read_text()
    object_map = (
        "PCFOLD1\n"
        "mode objects\n"
        "buildid object-merge\n"
        "sym ring_dispatch 0x1000 0x40\n"
        "sym legacy_worker 0x1040 0x40\n"
    )
    SYMAP.write_text(object_map)
    proc = subprocess.run(
        ["make", "-C", "/app/symmill", "emitmap"],
        check=False,
        capture_output=True,
        text=True,
    )
    SYMAP.write_text(original)
    PROFILE.write_text(profile_original)
    assert proc.returncode != 0


def test_premap19_symmap_index_origin():
    """Symmap must carry pcfold linked-index provenance, not a hand-built map."""
    lines = SYMAP.read_text().splitlines()
    assert "origin pcfold-index-linked" in lines


def test_premap21_pipeline_restores_linked_map():
    """Deleting fold artifacts and rerunning emitmap must restore a linked map."""
    SYMAP.unlink(missing_ok=True)
    PROFILE.unlink(missing_ok=True)
    proc = subprocess.run(
        ["make", "-C", "/app/symmill", "emitmap"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    lines = SYMAP.read_text().splitlines()
    assert "origin pcfold-index-linked" in lines
    _, _, span_by_name, meta = _parse_symmap()
    assert meta.get("mode") == "linked"
    expected = _nm_symbol_sizes()
    for name, span in span_by_name.items():
        assert name in expected
        assert span == expected[name]
