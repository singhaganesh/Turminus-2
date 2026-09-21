"""Verifier for flaxcord compact spins."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

BIN = Path("/app/bin/flaxcord")
DAY = Path("/app/spoolbay/day")
DUSK = Path("/app/spoolbay/dusk")
WELL = Path("/app/cordwell")
LIVE = WELL / "live.pfl"
ALT = WELL / "alt.pfl"
DIFF = WELL / "differ.txt"
OK = WELL / "spin.ok"


def _spin_with(exe: Path, src: Path, dst: Path) -> subprocess.CompletedProcess[str]:
    WELL.mkdir(parents=True, exist_ok=True)
    return subprocess.run(
        [str(exe), "spin", str(src), str(dst)],
        capture_output=True,
        text=True,
    )


def _spin(src: Path, dst: Path) -> subprocess.CompletedProcess[str]:
    WELL.mkdir(parents=True, exist_ok=True)
    return subprocess.run(
        ["/app/bin/flaxcord", "spin", str(src), str(dst)],
        capture_output=True,
        text=True,
    )


def _link_ref() -> Path:
    dest = Path("/tmp/flaxcord.ref")
    r = subprocess.run(
        ["make", "-C", "/app/flaxcli", "-f", "hull.mk", "OUT=/tmp/flaxcord.ref"],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    assert dest.is_file()
    return dest


def _unreel(path: Path) -> str:
    r = subprocess.run(
        ["/app/bin/flaxcord", "unreel", str(path)],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0
    return r.stdout


def _differ(a: Path, b: Path) -> str:
    subprocess.run(
        ["/app/bin/flaxcord", "differ", str(a), str(b)],
        capture_output=True,
        text=True,
    )
    return DIFF.read_text() if DIFF.exists() else ""


def _write_chk(folder: Path, name: str, seq: int, frames: list[str], hits: int, end: bool = True) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    body = [f"SEQ {seq}"] + frames + [f"HITS {hits}"]
    if end:
        body.append("END")
    (folder / name).write_text("\n".join(body) + "\n")


def test_fxv01_hdr():
    """Linked mill is ELF, matches a flaxcli hull of on-disk C, and two day spins match."""
    blob = BIN.read_bytes()
    assert blob[:4] == b"\x7fELF"
    ref = _link_ref()
    agent_pfl = WELL / "agent_day.pfl"
    ref_pfl = WELL / "ref_day.pfl"
    a = _spin(DAY, agent_pfl)
    b = _spin_with(ref, DAY, ref_pfl)
    assert a.returncode == 0
    assert b.returncode == 0
    assert agent_pfl.read_bytes() == ref_pfl.read_bytes()
    p1 = WELL / "t1.pfl"
    p2 = WELL / "t2.pfl"
    c = _spin(DAY, p1)
    d = _spin(DAY, p2)
    assert c.returncode == 0
    assert d.returncode == 0
    assert p1.read_bytes() == p2.read_bytes()


def test_fxv02_twin():
    """Second pair of process spins still matches on day."""
    p1 = WELL / "u1.pfl"
    p2 = WELL / "u2.pfl"
    assert _spin(DAY, p1).returncode == 0
    assert _spin(DAY, p2).returncode == 0
    assert p1.read_bytes() == p2.read_bytes()
    assert p1.stat().st_size > 8


def test_fxv03_pair():
    """Day and dusk compact files compare hush."""
    assert _spin(DAY, LIVE).returncode == 0
    assert _spin(DUSK, ALT).returncode == 0
    text = _differ(LIVE, ALT)
    assert "quiet" in DIFF.read_text()
    assert text.strip() == "quiet"


def test_fxv04_ord():
    """unreel lines are ordered by joined path."""
    assert _spin(DAY, LIVE).returncode == 0
    lines = [ln for ln in _unreel(LIVE).splitlines() if ln.strip()]
    keys = [ln.split(" COUNT ")[0] for ln in lines]
    assert keys == sorted(keys)
    assert any(ln.endswith("COUNT 4") for ln in lines)
    assert any(ln.endswith("COUNT 2") for ln in lines)
    assert any(ln.endswith("COUNT 3") for ln in lines)


def test_fxv05_hold():
    """Swapped SEQ holdout pair is hush."""
    ha = WELL / "ha"
    hb = WELL / "hb"
    shutil.rmtree(ha, ignore_errors=True)
    shutil.rmtree(hb, ignore_errors=True)
    _write_chk(ha, "a0.chk", 1, ["rho.nock"], 1)
    _write_chk(ha, "a1.chk", 2, ["alpha.tick"], 3)
    _write_chk(hb, "b0.chk", 1, ["alpha.tick"], 3)
    _write_chk(hb, "b1.chk", 2, ["rho.nock"], 1)
    oa = WELL / "ha.pfl"
    ob = WELL / "hb.pfl"
    assert _spin(ha, oa).returncode == 0
    assert _spin(hb, ob).returncode == 0
    assert _differ(oa, ob).strip() == "quiet"


def test_fxv06_tail():
    """Missing END makes spin exit non-zero."""
    bad = WELL / "bad"
    shutil.rmtree(bad, ignore_errors=True)
    _write_chk(bad, "z.chk", 1, ["omega.x"], 1, end=False)
    r = _spin(bad, WELL / "bad.pfl")
    assert r.returncode != 0


def test_fxv07_seal():
    """Missing END does not write spin.ok."""
    if OK.exists():
        OK.unlink()
    bad = WELL / "bad2"
    shutil.rmtree(bad, ignore_errors=True)
    _write_chk(bad, "z.chk", 1, ["omega.x"], 1, end=False)
    _spin(bad, WELL / "bad2.pfl")
    assert not OK.exists()


def test_fxv08_mint():
    """Corrupt live compact is restored by one spin of day."""
    WELL.mkdir(parents=True, exist_ok=True)
    LIVE.write_bytes(b"XXXX")
    r = _spin(DAY, LIVE)
    assert r.returncode == 0
    assert LIVE.read_bytes()[:4] == b"FLX1"
    p2 = WELL / "mint2.pfl"
    assert _spin(DAY, p2).returncode == 0
    assert LIVE.read_bytes() == p2.read_bytes()
    lines = [ln for ln in _unreel(LIVE).splitlines() if ln.strip()]
    keys = [ln.split(" COUNT ")[0] for ln in lines]
    assert keys == sorted(keys)


def test_fxv09_hits():
    """Second holdout permutation is hush."""
    ha = WELL / "hc"
    hb = WELL / "hd"
    shutil.rmtree(ha, ignore_errors=True)
    shutil.rmtree(hb, ignore_errors=True)
    _write_chk(ha, "c0.chk", 1, ["gamma.q"], 5)
    _write_chk(ha, "c1.chk", 2, ["beta.z"], 1)
    _write_chk(hb, "d0.chk", 1, ["beta.z"], 1)
    _write_chk(hb, "d1.chk", 2, ["gamma.q"], 5)
    oa = WELL / "hc.pfl"
    ob = WELL / "hd.pfl"
    assert _spin(ha, oa).returncode == 0
    assert _spin(hb, ob).returncode == 0
    assert _differ(oa, ob).strip() == "quiet"


def test_fxv10_child():
    """One spin child of dusk hush-compares with a spin of day."""
    assert _spin(DUSK, ALT).returncode == 0
    assert _spin(DAY, LIVE).returncode == 0
    assert _differ(LIVE, ALT).strip() == "quiet"


def test_fxv11_hush():
    """Two process day spins make differ write quiet."""
    x = WELL / "x.pfl"
    y = WELL / "y.pfl"
    assert _spin(DAY, x).returncode == 0
    assert _spin(DAY, y).returncode == 0
    text = _differ(x, y)
    assert text.strip() == "quiet"


def test_fxv12_peer():
    """unreel of day and dusk share joined paths and totals."""
    assert _spin(DAY, LIVE).returncode == 0
    assert _spin(DUSK, ALT).returncode == 0
    a = [ln for ln in _unreel(LIVE).splitlines() if ln.strip()]
    b = [ln for ln in _unreel(ALT).splitlines() if ln.strip()]
    assert a == b
    keys = [ln.split(" COUNT ")[0] for ln in a]
    assert keys == sorted(keys)
