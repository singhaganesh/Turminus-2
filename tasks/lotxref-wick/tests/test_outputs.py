"""Verifier for lotxref atlas rewrite and clip."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

BIN = Path("/app/bin/lotxref")
ATLAS = Path("/app/inkwell/span.atlas")
CLIP = Path("/app/inkwell/clip.out")
SHIFT = Path("/app/lotbay/shift.dmp")
TWIN = Path("/app/lotbay/twin.dmp")
PUMP = Path("/app/unitpit/alpha/pump.c")
UNIT = Path("/app/unitpit/gamma/shift.c")
LOTBAY = Path("/app/lotbay")
TANK = Path("/app/unitpit/beta/tank.c")

_ATLAS0 = ATLAS.read_bytes()
_UNIT0 = UNIT.read_text()
_PUMP0 = PUMP.read_text()
_LOTS0 = {p.name: p.read_bytes() for p in sorted(LOTBAY.glob("*.dmp"))}
_EXTRA_UNITS = (
    Path("/app/unitpit/gamma/held.c"),
    Path("/app/unitpit/alpha/extra.c"),
)


@pytest.fixture(autouse=True)
def _restore_desk():
    """Each case starts from the mill desk as it was when the verifier loaded."""
    ATLAS.write_bytes(_ATLAS0)
    UNIT.write_text(_UNIT0)
    PUMP.write_text(_PUMP0)
    for p in LOTBAY.glob("*.dmp"):
        if p.name not in _LOTS0:
            p.unlink()
    for name, data in _LOTS0.items():
        (LOTBAY / name).write_bytes(data)
    for extra in _EXTRA_UNITS:
        extra.unlink(missing_ok=True)
    yield
    ATLAS.write_bytes(_ATLAS0)
    UNIT.write_text(_UNIT0)
    PUMP.write_text(_PUMP0)


def _reknit() -> subprocess.CompletedProcess[str]:
    return subprocess.run(["/app/bin/lotxref", "reknit"], capture_output=True, text=True)


def _clip(path: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["/app/bin/lotxref", "clip", path], capture_output=True, text=True)


def _atlas_rows() -> list[str]:
    if not ATLAS.exists():
        return []
    lines = ATLAS.read_text().splitlines()
    return [ln for ln in lines[1:] if ln.strip()]


def test_aa_binary_magic_own_fn():
    """Linked mill is ELF and shift clip shows the origin function mark."""
    blob = BIN.read_bytes()
    assert blob.startswith(b"\x7fELF")
    r = _reknit()
    assert r.returncode == 0
    c = _clip(str(SHIFT))
    assert c.returncode == 0
    text = CLIP.read_text()
    assert "SHIFT_OWN" in text


def test_bb_cu_still_there():
    """Every atlas row after reknit names a file that still exists."""
    r = _reknit()
    assert r.returncode == 0
    for ln in _atlas_rows():
        parts = ln.split()
        assert len(parts) >= 4
        assert Path(parts[1]).is_file()


def test_cc_holdout_unit():
    """A unit added at grade time lands in the atlas and clips its own mark."""
    p = Path("/app/unitpit/gamma/held.c")
    p.write_text("void held_fn(void)\n{\n    /* HELD_MARK */\n}\n")
    dmp = Path("/app/lotbay/held.dmp")
    dmp.write_text("DUMP1\nheld_fn /app/unitpit/gamma/held.c 3\n")
    r = _reknit()
    assert r.returncode == 0
    c = _clip(str(dmp))
    assert c.returncode == 0
    assert "HELD_MARK" in CLIP.read_text()


def test_dd_absent_cu_dirty():
    """Hiding a dump origin makes reknit exit non-zero."""
    bak = UNIT.read_text()
    UNIT.unlink()
    r = _reknit()
    UNIT.write_text(bak)
    assert r.returncode != 0


def test_ee_twin_share_cu():
    """Twin helper names clip the dump origin mark, not the other unit."""
    r = _reknit()
    assert r.returncode == 0
    c = _clip(str(TWIN))
    assert c.returncode == 0
    text = CLIP.read_text()
    assert "ALPHA_MARK" in text
    assert "BETA_MARK" not in text


def _row_names_unit(name: str, unit: Path) -> bool:
    want = str(unit)
    for ln in _atlas_rows():
        parts = ln.split()
        if len(parts) >= 4 and parts[0] == name and parts[1] == want:
            return True
    return False


def test_ff_corrupt_then_regen():
    """Trashing the atlas and rerunning reknit restores shift clip and off-list units."""
    ATLAS.write_text("SPAN1\n")
    r = subprocess.run(["/app/bin/lotxref", "reknit"], capture_output=True, text=True)
    assert r.returncode == 0
    c = _clip(str(SHIFT))
    assert c.returncode == 0
    assert "SHIFT_OWN" in CLIP.read_text()
    assert _row_names_unit("tank_drain", TANK)
    assert _row_names_unit("pump_fill", PUMP)


def test_gg_lead_moves_mark():
    """Leading comments then reknit still clips the origin function mark."""
    raw = UNIT.read_text()
    UNIT.write_text("/* lead */\n" * 10 + raw)
    r = _reknit()
    assert r.returncode == 0
    c = _clip(str(SHIFT))
    UNIT.write_text(raw)
    assert c.returncode == 0
    assert "SHIFT_OWN" in CLIP.read_text()


def test_hh_cu_body_token():
    """clip.out for the twin dump starts with CLIP and the origin token."""
    r = _reknit()
    assert r.returncode == 0
    c = _clip(str(TWIN))
    assert c.returncode == 0
    text = CLIP.read_text()
    assert text.startswith("CLIP helper_q")
    assert "ALPHA_MARK" in text


def test_ii_holdout_twin():
    """A third live helper_q added at grade time clips its own mark."""
    p = Path("/app/unitpit/alpha/extra.c")
    p.write_text("void helper_q(void)\n{\n    /* HOLD_MARK */\n}\n")
    dmp = Path("/app/lotbay/holdq.dmp")
    dmp.write_text("DUMP1\nhelper_q /app/unitpit/alpha/extra.c 3\n")
    r = _reknit()
    assert r.returncode == 0
    c = _clip(str(dmp))
    assert c.returncode == 0
    text = CLIP.read_text()
    assert "HOLD_MARK" in text
    assert "BETA_MARK" not in text


def test_rr_idle_absent():
    """Shift clip must not emit the neighbour idle mark."""
    r = _reknit()
    assert r.returncode == 0
    c = _clip(str(SHIFT))
    assert c.returncode == 0
    text = CLIP.read_text()
    assert "IDLE_MARK" not in text
    assert "SHIFT_OWN" in text


def test_nn_hidden_keeps_prior():
    """Failed reknit leaves the previous atlas bytes in place."""
    _reknit()
    prior = ATLAS.read_bytes()
    bak = UNIT.read_text()
    UNIT.unlink()
    r = _reknit()
    now = ATLAS.read_bytes()
    UNIT.write_text(bak)
    assert r.returncode != 0
    assert now == prior


def test_pp_second_cu_dirty():
    """Hiding a different dump origin also makes reknit exit non-zero."""
    bak = PUMP.read_text()
    PUMP.unlink()
    r = _reknit()
    PUMP.write_text(bak)
    assert r.returncode != 0


def test_qq_restore_then_clean():
    """After restoring a hidden origin, reknit returns success."""
    bak = UNIT.read_text()
    UNIT.unlink()
    dirty = _reknit()
    UNIT.write_text(bak)
    clean = _reknit()
    assert dirty.returncode != 0
    assert clean.returncode == 0
