"""Verifier for pinweld census and poke artifacts."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

BIN = Path("/app/bin/pinweld")
WELD = Path("/app/ribunit")
STOCK = WELD / "stock"
WELL = Path("/app/mintbay")
REG = WELL / "points.reg"
LST = WELL / "runtime.lst"
LOG = WELL / "scan.log"


@pytest.fixture(autouse=True)
def _restore():
    for p in WELD.glob("*.c"):
        p.unlink()
    for p in STOCK.glob("*"):
        shutil.copy(p, WELD / p.name)
    yield


def _census() -> subprocess.CompletedProcess[str]:
    return subprocess.run(["/app/bin/pinweld", "census"], capture_output=True, text=True)


def _poke(name: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["/app/bin/pinweld", "poke", name], capture_output=True, text=True)


def _names(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [ln.strip() for ln in path.read_text().splitlines() if ln.strip()]


def test_pws01_elf_stock_mark():
    """Linked mill is ELF and stock salvage-path mark lands after one census."""
    blob = BIN.read_bytes()
    assert blob[:4] == b"\x7fELF"
    r = _census()
    assert r.returncode == 0
    assert "salvage_drain" in _names(REG)


def test_pws02_one_pass_union():
    """One census subprocess lists core, salvage-path, and dusk marks together."""
    r = _census()
    assert r.returncode == 0
    got = set(_names(REG))
    assert {"core_pump", "salvage_drain", "night_lamp"} <= got


def test_pws03_holdout_gated_lands():
    """A fresh salvage-gated declaration added at grade time lands after one census."""
    p = WELD / "salvage.c"
    p.write_text(p.read_text() + "\n#ifdef SALVAGE\nWELD_HOOK(held_guard);\n#endif\n")
    r = _census()
    assert r.returncode == 0
    assert "held_guard" in _names(REG)


def test_pws04_absent_exits_dirty():
    """Declared shipped mark absent from the registry makes census fail."""
    p = WELD / "salvage.c"
    p.write_text(p.read_text() + "\n#ifdef SALVAGE\nWELD_HOOK(held_two);\n#endif\n")
    r = _census()
    names = _names(REG)
    if "held_two" not in names:
        assert r.returncode != 0
    assert "held_two" in names
    assert r.returncode == 0


def test_pws05_fire_guard_stdout():
    """poke fires the salvage-path mark once the runtime list holds it."""
    assert _census().returncode == 0
    r = _poke("salvage_drain")
    assert r.returncode == 0
    line = r.stdout.strip()
    assert line.startswith("fired:")
    assert line.split(":", 1)[1] == "salvage_drain"


def test_pws06_corrupt_then_mint():
    """Corrupt mintbay products then one census restores the union."""
    assert _census().returncode == 0
    REG.write_text("core_pump\n")
    LST.write_text("core_pump\n")
    r = _census()
    assert r.returncode == 0
    got = set(_names(REG))
    assert {"core_pump", "salvage_drain", "night_lamp"} <= got
    assert _names(REG) == _names(LST)


def test_pws07_dusk_mark_present():
    """Night recipe mark is present without copying it into the core unit."""
    r = _census()
    assert r.returncode == 0
    assert "night_lamp" in _names(REG)
    night = (WELD / "night.c").read_text()
    assert "WELD_HOOK(night_lamp)" in night
    assert "#ifdef NIGHT" in night


def test_pws08_log_names_unit():
    """scan.log names the salvage unit even when that mark must also be in the registry."""
    r = _census()
    assert r.returncode == 0
    text = LOG.read_text()
    assert "ribunit/salvage.c" in text
    assert "salvage_drain" in _names(REG)


def test_pws09_lst_matches_reg():
    """runtime.lst independently matches points.reg line-for-line after census."""
    assert _census().returncode == 0
    assert _names(LST) == _names(REG)
    assert _names(REG) == sorted(_names(REG))


def test_pws10_pair_fresh_both():
    """Two newly added gated declarations both land from a single census subprocess."""
    s = WELD / "salvage.c"
    n = WELD / "night.c"
    s.write_text(s.read_text() + "\n#ifdef SALVAGE\nWELD_HOOK(fresh_one);\n#endif\n")
    n.write_text(n.read_text() + "\n#ifdef NIGHT\nWELD_HOOK(fresh_two);\n#endif\n")
    r = _census()
    assert r.returncode == 0
    got = set(_names(REG))
    assert "fresh_one" in got and "fresh_two" in got


def test_pws11_second_mint_same():
    """Two census runs write identical registries."""
    assert _census().returncode == 0
    first = REG.read_text()
    assert _census().returncode == 0
    assert REG.read_text() == first


def test_pws12_core_stays():
    """Always-on core mark remains after census."""
    r = _census()
    assert r.returncode == 0
    assert "core_pump" in _names(REG)


def test_pws13_unshipped_omitted():
    """Marks not visible under any shipped recipe stay out of the registry."""
    r = _census()
    assert r.returncode == 0
    got = set(_names(REG))
    assert "lab_ghost" not in got
    assert "dead_zero" not in got
