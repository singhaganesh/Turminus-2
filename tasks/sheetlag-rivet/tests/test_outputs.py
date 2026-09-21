"""Verifier for rivetbay mill and decode artifacts."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

_APP = "/app/rivetbay"
EVD = Path(_APP) / "evd"
LEDGER = Path(_APP) / "intake" / "current.ledger"
MILL_PASS = Path(_APP) / "intake" / ".mill_pass"
EMIT = Path(_APP) / "emitters"
FRAMES = Path(_APP) / "frames"
SEED = Path(_APP) / "seed"
_MILL_OPEN = Path(_APP) / "intake" / "mill_open"
_SEED_LEDGER_ROWS = [
    ln for ln in (SEED / "intake" / "current.ledger").read_text().splitlines() if ln.strip()
]


@pytest.fixture(autouse=True)
def _restore_bench():
    for dst, sub in ((EVD, "evd"), (EMIT, "emitters"), (FRAMES, "frames")):
        for p in dst.glob("*"):
            if p.is_file():
                p.unlink()
        for p in (SEED / sub).glob("*"):
            shutil.copy(p, dst / p.name)
    shutil.copy(SEED / "intake" / "current.ledger", LEDGER)
    shutil.copy(SEED / "intake" / "mill_open", _MILL_OPEN)
    if MILL_PASS.exists():
        MILL_PASS.unlink()
    yield


def _evd_names() -> set[str]:
    return {p.stem for p in EVD.glob("*.evd")}


def _kdec_names() -> set[str]:
    return {p.stem for p in EMIT.glob("*.kdec")}


def _mill() -> subprocess.CompletedProcess[str]:
    return subprocess.run(["/app/bin/rivetbay", "mill"], capture_output=True, text=True)


def _decode(frame: Path) -> dict:
    r = subprocess.run(
        ["/app/bin/rivetbay", "decode", str(frame)], capture_output=True, text=True, check=True
    )
    return json.loads(r.stdout.strip().splitlines()[-1])


def _write_evd(name: str, fields: list[tuple[str, str]]) -> None:
    lines = [f"NAME {name}"] + [f"FIELD {f} {k}" for f, k in fields]
    (EVD / f"{name}.evd").write_text("\n".join(lines) + "\n")


def _write_frame(name: str, fields: list[tuple[str, str]], values: dict[str, int]) -> Path:
    body = b""
    for f, k in fields:
        v = values[f]
        body += int(v).to_bytes(2, "big") if k == "u16" else int(v).to_bytes(1, "big")
    nb = name.encode()
    path = FRAMES / f"{name}.bin"
    path.write_bytes(len(nb).to_bytes(4, "big") + nb + body)
    return path


def _ledger_stems() -> set[str]:
    return {ln.split("|", 1)[0] for ln in LEDGER.read_text().splitlines() if ln.strip()}


def _mill_pass_count() -> int:
    if not MILL_PASS.exists():
        return 0
    return len([ln for ln in MILL_PASS.read_text().splitlines() if ln.strip()])


def test_mill_subprocess_runs_once():
    """One mill subprocess must succeed and execute the mill body exactly once."""
    r = _mill()
    assert _mill_pass_count() == 1
    assert r.returncode == 0
    assert _evd_names() == _kdec_names()


def test_brand_new_description_single_mill():
    """A description added with no prior mill must receive a decoder from one subprocess."""
    name = "nova_spark"
    fields = [("volt", "u16")]
    _write_evd(name, fields)
    r = _mill()
    assert _mill_pass_count() == 1
    assert r.returncode == 0
    assert name in _kdec_names()
    assert _evd_names() == _kdec_names()


def test_mill_once_matches_descriptions():
    """One mill must emit a decoder for every description currently on disk."""
    r = _mill()
    assert r.returncode == 0
    assert _evd_names() == _kdec_names()


def test_stock_gap_event_gets_decoder():
    """The description that shipped without a decoder must appear under emitters after one mill."""
    assert _mill().returncode == 0
    assert "galley_hatch" in _kdec_names()


def test_stock_gap_event_decodes_fields():
    """The shipped gap event must decode to its latch and force fields after one mill."""
    assert _mill().returncode == 0
    data = _decode(FRAMES / "galley_hatch.bin")
    assert data["kind"] == "decoded"
    assert data["name"] == (FRAMES / "galley_hatch.bin").stem
    assert data["fields"] == {"latch": 1, "force": 44}


def test_new_event_decodes_fields():
    """A description added before mill must decode to its integer fields after that mill."""
    name = "zulu_glow"
    fields = [("amp", "u16"), ("bit", "u8")]
    _write_evd(name, fields)
    frame = _write_frame(name, fields, {"amp": 9, "bit": 4})
    r = _mill()
    assert _mill_pass_count() == 1
    assert r.returncode == 0
    data = _decode(frame)
    assert data["kind"] == "decoded"
    assert data["name"] == name
    assert data["fields"] == {"amp": 9, "bit": 4}


def test_mill_exit_tracks_counts():
    """Mill must exit non-zero when fewer decoders than descriptions remain after the pass."""
    r = _mill()
    evd, kdec = _evd_names(), _kdec_names()
    if len(kdec) < len(evd):
        assert r.returncode != 0
    else:
        assert r.returncode == 0
        assert evd == kdec


def test_unknown_stays_for_nameless_frame():
    """After mill closes description gaps, a frame with no description still decodes as unknown."""
    assert _mill().returncode == 0
    assert "galley_hatch" in _kdec_names()
    data = _decode(_write_frame("ghost_wire", [("x", "u8")], {"x": 1}))
    assert data == {"kind": "unknown", "name": "ghost_wire"}


def test_held_out_pair_single_mill():
    """Two newly added descriptions must both receive decoders from a single mill."""
    a = ("amber_web", [("n", "u8")])
    b = ("quartz_lid", [("w", "u16")])
    _write_evd(*a)
    _write_evd(*b)
    r = _mill()
    assert _mill_pass_count() == 1
    assert r.returncode == 0
    assert a[0] in _kdec_names() and b[0] in _kdec_names()
    assert _evd_names() == _kdec_names()


def test_ledger_matches_emitters_and_evd():
    """After mill, ledger stems, decoder stems, and description stems are the same set."""
    assert _mill().returncode == 0
    assert _ledger_stems() == _evd_names() == _kdec_names()


def test_kdec_header_for_gap_event():
    """The gap event's decoder must use the KDEC1 grammar after one mill."""
    assert _mill().returncode == 0
    assert "KDEC1" in (EMIT / "galley_hatch.kdec").read_text()
    text = (EMIT / "galley_hatch.kdec").read_text().splitlines()
    assert text[0] == "KDEC1"
    assert text[1] == "NAME galley_hatch"
    assert "latch u8" in text
    assert "force u16" in text


def test_old_and_new_together():
    """After one mill, a prior sample still decodes and the gap event is no longer unknown."""
    assert _mill().returncode == 0
    old = _decode(FRAMES / "wing_ice.bin")
    new = _decode(FRAMES / "galley_hatch.bin")
    assert old["kind"] == "decoded" and old["name"] == (FRAMES / "wing_ice.bin").stem
    assert new["kind"] == "decoded" and new["name"] == (FRAMES / "galley_hatch.bin").stem


def test_held_out_json_kind():
    """Held-out decode uses kind decoded, not unknown, after one mill."""
    name = "iota_clip"
    fields = [("q", "u8")]
    _write_evd(name, fields)
    frame = _write_frame(name, fields, {"q": 7})
    assert _mill().returncode == 0
    data = _decode(frame)
    assert data["kind"] == "decoded"
    assert data["fields"]["q"] == 7


def test_held_out_u16_layout():
    """A held-out u16 field must round-trip through one mill and decode."""
    name = "mica_beam"
    fields = [("mm", "u16")]
    _write_evd(name, fields)
    frame = _write_frame(name, fields, {"mm": 1000})
    assert _mill().returncode == 0
    assert _decode(frame)["fields"]["mm"] == 1000


def test_gap_event_is_last_ledger_row():
    """After one mill the gap description must be the final ledger row with a decoder."""
    assert _mill().returncode == 0
    assert "galley_hatch" in _kdec_names()
    rows = [ln for ln in LEDGER.read_text().splitlines() if ln.strip()]
    assert rows[-1].startswith("galley_hatch|")


def test_two_fresh_descriptions_both_decode():
    """Two descriptions added together must both decode after a single mill."""
    specs = [
        ("opal_ring", [("hue", "u8")], {"hue": 3}),
        ("velvet_pin", [("len", "u16")], {"len": 512}),
    ]
    for name, fields, _ in specs:
        _write_evd(name, fields)
    r = _mill()
    assert _mill_pass_count() == 1
    assert r.returncode == 0
    for name, fields, values in specs:
        frame = _write_frame(name, fields, values)
        data = _decode(frame)
        assert data["kind"] == "decoded"
        assert data["fields"] == values


def test_second_mill_picks_up_new_description():
    """A description added after an earlier mill must decode after one later mill."""
    assert _mill().returncode == 0
    name = "cobalt_arc"
    fields = [("phase", "u8")]
    _write_evd(name, fields)
    frame = _write_frame(name, fields, {"phase": 11})
    assert _mill().returncode == 0
    data = _decode(frame)
    assert data["kind"] == "decoded"
    assert data["fields"] == {"phase": 11}


def test_mill_idempotent_twice():
    """Two consecutive mills must keep emitters aligned with descriptions."""
    assert _mill().returncode == 0
    assert _mill().returncode == 0
    assert _evd_names() == _kdec_names()
    data = _decode(FRAMES / "galley_hatch.bin")
    assert data["kind"] == "decoded"
    assert data["fields"] == {"latch": 1, "force": 44}


def test_field_order_sensitive_decode():
    """Decoder field lines must follow description order, not alphabetical order."""
    name = "theta_slot"
    fields = [("z_delta", "u8"), ("alpha_mm", "u16")]
    values = {"z_delta": 5, "alpha_mm": 1700}
    _write_evd(name, fields)
    frame = _write_frame(name, fields, values)
    r = _mill()
    assert _mill_pass_count() == 1
    assert r.returncode == 0
    data = _decode(frame)
    assert data["kind"] == "decoded"
    assert data["fields"] == values


def test_ledger_preserves_seed_prefix():
    """Prior ledger rows must stay in seed order when new descriptions are appended."""
    _write_evd("opal_ring", [("hue", "u8")])
    _write_evd("velvet_pin", [("len", "u16")])
    assert _mill().returncode == 0
    assert _evd_names() == _kdec_names()
    rows = [ln for ln in LEDGER.read_text().splitlines() if ln.strip()]
    assert len(rows) >= len(_SEED_LEDGER_ROWS) + 2
    for idx, seed_row in enumerate(_SEED_LEDGER_ROWS):
        assert rows[idx] == seed_row


def test_u16_boundary_values_decode():
    """Held-out u16 boundary values must round-trip through mill and decode."""
    cases = [
        ("zero_span", [("span", "u16")], {"span": 0}),
        ("full_span", [("span", "u16")], {"span": 65535}),
    ]
    for name, fields, values in cases:
        _write_evd(name, fields)
        frame = _write_frame(name, fields, values)
    assert _mill().returncode == 0
    for name, fields, values in cases:
        frame = _write_frame(name, fields, values)
        data = _decode(frame)
        assert data["kind"] == "decoded"
        assert data["fields"] == values
