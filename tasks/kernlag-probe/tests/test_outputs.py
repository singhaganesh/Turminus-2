"""Kernlag contract verifier."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

LAYOUT = Path("/app/lagpipe/synctab_out/layout.tbl")
PROCANCE = Path("/app/lagpipe/synctab_out/procance.tag")
GUARD = Path("/app/lagpipe/synctab_out/offline_guard.ok")
LIVE_EXPORT = Path("/app/livekern/exports/sched_entity.tab")
RUNNING = Path("/app/livekern/running.release")
LANES = Path("/app/memvault/samples")
CARDS = Path("/app/memvault/cards")
LANE_A = LANES / "pulse_a.mem"
LANE_B = LANES / "pulse_b.mem"
LANE_C = LANES / "pulse_c.mem"
LAGPICK = Path("/app/relc/input.c")
ORIGIN_FIXTURE = Path("/app/memvault/regression/bundle_pick_input.c")
SYNCTAB = ["/app/bin/kernscribe", "synctab"]
LINK = ["make", "-C", "/app/lagpipe", "bind"]


def _release() -> str:
    return RUNNING.read_text().strip()


def _inspect(capture: Path) -> dict:
    r = subprocess.run(
        ["/app/bin/kernscribe", "inspect", str(capture)],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(r.stdout.strip())


def _card(stem: str) -> dict:
    return json.loads((CARDS / f"{stem}.ref").read_text())


def _field_lines(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text().splitlines() if line.startswith("FIELD ")]


def _live_export_layout() -> tuple[str, list[tuple[str, str, int, int]]]:
    struct_name = "sched_entity"
    fields: list[tuple[str, str, int, int]] = []
    for line in LIVE_EXPORT.read_text().splitlines():
        if line.startswith("STRUCT "):
            struct_name = line.split()[1]
        elif line.startswith("FIELD "):
            parts = line.split()
            fields.append((parts[1], parts[2], int(parts[3]), int(parts[4])))
    return struct_name, fields


def _read_u32(blob: bytes, off: int) -> int:
    return (
        blob[off]
        | (blob[off + 1] << 8)
        | (blob[off + 2] << 16)
        | (blob[off + 3] << 24)
    )


def _read_u64(blob: bytes, off: int) -> int:
    return _read_u32(blob, off) | (_read_u32(blob, off + 4) << 32)


def _expected_from_live_export(capture: Path) -> dict:
    """Recompute inspect JSON from capture bytes and live-export field layout."""
    blob = capture.read_bytes()
    struct_name, fields = _live_export_layout()
    out: dict[str, object] = {"struct": struct_name}
    for name, kind, off, _size in fields:
        if kind == "u64":
            out[name] = _read_u64(blob, off)
        else:
            out[name] = _read_u32(blob, off)
    return out


def _run_synctab() -> subprocess.CompletedProcess[str]:
    return subprocess.run(SYNCTAB, capture_output=True, text=True, check=False)


def test_klg01_tag_live():
    """procance.tag must be live: plus the running.release value after synctab."""
    tag = PROCANCE.read_text().strip()
    assert tag == f"live:{_release()}"


def test_klg02_pulse_a():
    """pulse_a inspect JSON must equal pulse_a.ref."""
    assert _inspect(LANE_A) == _card("pulse_a")


def test_klg03_pulse_b():
    """Held-out pulse_b capture must match its reference card."""
    assert _inspect(LANE_B) == _card("pulse_b")


def test_klg04_order_d():
    """layout.tbl must include migration_flags between weight and slice_ns."""
    body = LAYOUT.read_text()
    assert "FIELD migration_flags u32 8 4" in body
    assert body.index("migration_flags") < body.index("slice_ns")


def test_klg05_guard_ok():
    """Successful synctab must leave offline_guard.ok enforced."""
    assert GUARD.read_text().strip() == "1"


def test_klg06_all_pulses():
    """Every memvault sample must match its sibling reference card."""
    for capture in sorted(LANES.glob("*.mem")):
        ref = CARDS / f"{capture.stem}.ref"
        if not ref.is_file():
            continue
        assert _inspect(capture) == _card(capture.stem)


def test_klg07_live_parity():
    """synctab_out layout.tbl field lines must match the livekern export."""
    assert _field_lines(LAYOUT) == _field_lines(LIVE_EXPORT)


def test_klg08_stamp_prefix():
    """procance.tag must record live: not bundle: after repair."""
    tag = PROCANCE.read_text().strip()
    assert tag.startswith("live:")


def test_klg09_pulse_a_mig():
    """pulse_a migration_flags must match its reference card."""
    assert _inspect(LANE_A)["migration_flags"] == _card("pulse_a")["migration_flags"]


def test_klg10_pulse_a_slice():
    """pulse_a slice_ns must match its reference card."""
    assert _inspect(LANE_A)["slice_ns"] == _card("pulse_a")["slice_ns"]


def test_klg11_pulse_b_slice():
    """Held-out pulse_b slice_ns must match its reference card."""
    assert _inspect(LANE_B)["slice_ns"] == _card("pulse_b")["slice_ns"]


def test_klg12_json_keys():
    """inspect JSON must expose pid, weight, migration_flags, and slice_ns."""
    keys = set(_inspect(LANE_A).keys())
    assert keys == {"struct", "pid", "weight", "migration_flags", "slice_ns"}


def test_klg13_four_fields():
    """layout.tbl must publish four sched_entity fields from the live export."""
    assert len(_field_lines(LAYOUT)) == 4
    assert len(_field_lines(LIVE_EXPORT)) == 4


def test_klg14_pick_reject():
    """synctab must exit non-zero when layout pick would record a bundle origin."""
    saved = LAGPICK.read_bytes()
    GUARD.unlink(missing_ok=True)
    LAGPICK.write_bytes(ORIGIN_FIXTURE.read_bytes())
    subprocess.run(LINK, check=True)
    proc = _run_synctab()
    assert proc.returncode != 0
    assert not GUARD.exists()
    LAGPICK.write_bytes(saved)
    subprocess.run(LINK, check=True)
    assert _run_synctab().returncode == 0


def test_klg15_holdout_pulse_c():
    """Recompute held-out pulse_c inspect JSON from live-export layout rules."""
    assert _inspect(LANE_C) == _expected_from_live_export(LANE_C)


def test_klg16_holdout_pulse_c_migration():
    """Held-out pulse_c migration_flags must follow live-export offset rules."""
    assert _inspect(LANE_C)["migration_flags"] == _expected_from_live_export(LANE_C)["migration_flags"]


def test_klg17_holdout_pulse_c_slice():
    """Held-out pulse_c slice_ns must follow live-export offset rules."""
    assert _inspect(LANE_C)["slice_ns"] == _expected_from_live_export(LANE_C)["slice_ns"]


def test_klg_zz_stamp_recovery():
    """synctab must rebuild synctab_out after corrupt hand-written layout artifacts."""
    LAYOUT.write_text("STRUCT sched_entity\nFIELD pid u32 0 4\nFIELD weight u32 4 4\n")
    PROCANCE.write_text("bundle:6.8.12\n")
    GUARD.write_text("1\n")
    proc = _run_synctab()
    assert proc.returncode == 0
    assert "FIELD migration_flags u32 8 4" in LAYOUT.read_text()
    assert PROCANCE.read_text().strip() == f"live:{_release()}"
    assert GUARD.read_text().strip() == "1"
    assert _inspect(LANE_A) == _card("pulse_a")
    assert _inspect(LANE_C) == _expected_from_live_export(LANE_C)
