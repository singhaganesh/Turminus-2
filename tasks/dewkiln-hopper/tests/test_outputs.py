"""Verifier for dewkiln clasp artifacts."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

BIN = Path("/app/bin/dewkiln")
DAY = Path("/app/daywell")
SEED = Path("/app/seed/daywell")
BLO = Path("/app/bloturn")
LEDGER = BLO / "ledger.json"
CHECK = BLO / "check.json"
GUARD = BLO / "GUARD"
LATEST = Path("/app/packbay/latest")
STAGE = Path("/app/packbay/stage")
WALL = int(Path("/app/opstext/WALL").read_text().strip())
TPL = Path("/app/millrib/sheet.tpl")


def _assert_native() -> None:
    assert BIN.read_bytes()[:4] == b"\x7fELF"


def _nlines(path: Path) -> int:
    if not path.is_file():
        return 0
    return sum(1 for line in path.read_text().splitlines() if line.strip())


def _restore() -> None:
    DAY.mkdir(parents=True, exist_ok=True)
    for p in DAY.glob("*.tbl"):
        p.unlink()
    for p in SEED.glob("*.tbl"):
        shutil.copy(p, DAY / p.name)


def _clasp() -> subprocess.CompletedProcess[str]:
    _assert_native()
    return subprocess.run(
        ["/app/bin/dewkiln", "clasp"],
        capture_output=True,
        text=True,
    )


def _live_newest() -> tuple[int, int]:
    days = []
    for p in DAY.glob("d*.tbl"):
        d = int(p.name[1:9])
        if d <= WALL:
            days.append(d)
    assert days
    n = max(days)
    return n, _nlines(DAY / f"d{n:08d}.tbl")


def _load_check() -> dict:
    return json.loads(CHECK.read_text())


def test_dk01_twice_blob():
    """Two clasp processes write identical latest names matching the stage set."""
    _restore()
    r1 = _clasp()
    assert r1.returncode == 0
    names1 = sorted(p.name for p in LATEST.glob("*.tbl"))
    stage1 = sorted(p.name for p in STAGE.glob("*.tbl"))
    assert names1 == stage1
    assert names1
    blob1 = CHECK.read_bytes()
    r2 = _clasp()
    assert r2.returncode == 0
    names2 = sorted(p.name for p in LATEST.glob("*.tbl"))
    assert names2 == names1
    assert CHECK.read_bytes() == blob1


def test_dk02_held_extra():
    """An older held-out day file is unpacked; a day past the wall is not."""
    _restore()
    (DAY / "d20260908.tbl").write_text("11\n12\n")
    (DAY / "d20260914.tbl").write_text("91\n92\n93\n")
    r = _clasp()
    assert r.returncode == 0
    assert (LATEST / "d20260908.tbl").is_file()
    assert _nlines(LATEST / "d20260908.tbl") == 2
    assert not (LATEST / "d20260914.tbl").is_file()
    n, live = _live_newest()
    assert n == WALL
    assert _nlines(LATEST / f"d{n:08d}.tbl") == live
    _restore()


def test_dk03_cur_pack():
    """Restored row count for the wall day equals the daywell count."""
    _restore()
    assert _clasp().returncode == 0
    n, live = _live_newest()
    assert _nlines(LATEST / f"d{n:08d}.tbl") == live
    assert live > 0


def test_dk04_kind_word():
    """check.json probe is live after clasp."""
    _restore()
    assert _clasp().returncode == 0
    data = _load_check()
    assert data["probe"] == "live"


def test_dk05_solo_today():
    """A daywell that holds only the wall file still unpacks those rows."""
    _restore()
    keep = DAY / f"d{WALL:08d}.tbl"
    blob = keep.read_bytes()
    for p in DAY.glob("*.tbl"):
        p.unlink()
    keep.write_bytes(blob)
    r = _clasp()
    assert r.returncode == 0
    assert _nlines(LATEST / f"d{WALL:08d}.tbl") == _nlines(keep)
    _restore()


def test_dk06_hdr_magic():
    """dewkiln is ELF and the wall day survives clasp."""
    _restore()
    _assert_native()
    assert _clasp().returncode == 0
    n, live = _live_newest()
    assert _nlines(LATEST / f"d{n:08d}.tbl") == live


def test_dk07_stamp_text():
    """GUARD is ok on a live check; empty daywell leaves GUARD absent."""
    _restore()
    r = _clasp()
    data = _load_check()
    if data.get("probe") != "live":
        assert r.returncode != 0
        assert not GUARD.exists()
        raise AssertionError("probe is not live")
    assert r.returncode == 0
    assert GUARD.read_text() == "ok"
    for p in DAY.glob("*.tbl"):
        p.unlink()
    r2 = _clasp()
    assert r2.returncode != 0
    assert not GUARD.exists()
    _restore()


def test_dk08_ahead_omit():
    """A day past the wall stays out of latest while the wall day stays in."""
    _restore()
    (DAY / "d20260914.tbl").write_text("77\n")
    assert _clasp().returncode == 0
    assert not (LATEST / "d20260914.tbl").is_file()
    assert _nlines(LATEST / f"d{WALL:08d}.tbl") == _nlines(DAY / f"d{WALL:08d}.tbl")
    _restore()


def test_dk09_keys_obj():
    """matched equals the live sum for days at or before the wall."""
    _restore()
    assert _clasp().returncode == 0
    data = _load_check()
    assert data["probe"] == "live"
    live_sum = 0
    for p in DAY.glob("d*.tbl"):
        d = int(p.name[1:9])
        if d <= WALL:
            live_sum += _nlines(p)
    assert data["matched"] == live_sum
    assert data["taken"] == live_sum
    assert set(data) >= {"probe", "matched", "taken"}


def test_dk10_zz_corrupt():
    """Hand-broken bloturn files are rebuilt by a later clasp."""
    _restore()
    assert _clasp().returncode == 0
    CHECK.write_text("{}")
    LEDGER.write_text("{}")
    r = _clasp()
    assert r.returncode == 0
    data = _load_check()
    assert data["probe"] == "live"
    n, live = _live_newest()
    assert _nlines(LATEST / f"d{n:08d}.tbl") == live
    assert TPL.read_text().count("__P__") == 1


def test_dk11_once_pass():
    """One clasp subprocess unpacks every staged shard."""
    _restore()
    r = _clasp()
    assert r.returncode == 0
    stage = sorted(p.name for p in STAGE.glob("*.tbl"))
    latest = sorted(p.name for p in LATEST.glob("*.tbl"))
    assert latest == stage
    assert f"d{WALL:08d}.tbl" in latest


def test_dk12_floor_ignored():
    """Newest-day parity holds even when taken already clears the CI floor."""
    _restore()
    floor = int(Path("/app/floorcue/MIN.txt").read_text().strip())
    assert _clasp().returncode == 0
    data = _load_check()
    assert data["probe"] == "live"
    n, live = _live_newest()
    assert _nlines(LATEST / f"d{n:08d}.tbl") == live
    assert data["taken"] >= floor
