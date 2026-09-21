"""Verifier for keelgrip heap ledgers."""

from __future__ import annotations

import subprocess
from pathlib import Path

BIN = Path("/app/bin/keelgrip")
DAY = Path("/app/packurn/day.hpk")
DUSK = Path("/app/packurn/dusk.hpk")
WELL = Path("/app/inkurn")
LIVE = WELL / "live.txt"
ALT = WELL / "alt.txt"
NOTE = WELL / "align.txt"
OK = WELL / "mint.ok"


def _retain_path(root: str, *hops: str) -> str:
    return "PATH " + root + ">" + ">".join(hops)


def _day_path() -> str:
    return _retain_path("JNI", "Mule.slot", "Leak.item")


def _hold_path() -> str:
    return _retain_path("JNI", "Keg.other", "Leak.item")


def _mint_with(exe: Path, src: Path, dst: Path) -> subprocess.CompletedProcess[str]:
    WELL.mkdir(parents=True, exist_ok=True)
    return subprocess.run(
        [str(exe), "mint", str(src), str(dst)],
        capture_output=True,
        text=True,
    )


def _mint(src: Path, dst: Path) -> subprocess.CompletedProcess[str]:
    WELL.mkdir(parents=True, exist_ok=True)
    return subprocess.run(
        ["/app/bin/keelgrip", "mint", str(src), str(dst)],
        capture_output=True,
        text=True,
    )


def _link_ref() -> Path:
    dest = Path("/tmp/keelgrip.ref")
    r = subprocess.run(
        ["make", "-C", "/app/millarm", "-f", "driver.mk", "OUT=/tmp/keelgrip.ref"],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    assert dest.is_file()
    return dest


def _align(a: Path, b: Path) -> str:
    subprocess.run(
        ["/app/bin/keelgrip", "align", str(a), str(b)],
        capture_output=True,
        text=True,
    )
    return NOTE.read_text() if NOTE.exists() else ""


def _path_line(text: str) -> str:
    for ln in text.splitlines():
        if ln.startswith("PATH "):
            return ln
    return ""


def _write_hpk(path: Path, mule: int, noll: int, mule_cls: str, noll_cls: str) -> None:
    body = f"""HPK1
NODE 10 JNIRoot 16
NODE 20 VRoot 16
NODE 30 Anchor 32
NODE {mule} {mule_cls} 48
NODE {noll} {noll_cls} 48
NODE 60 Leak 128
EDGE 10 30 STRONG box
EDGE 10 {mule} STRONG slot
EDGE 10 {noll} STRONG other
EDGE 30 60 WEAK ghost
EDGE {mule} 60 STRONG item
EDGE {noll} 60 STRONG item
EDGE 20 {mule} STRONG via
EDGE 20 {noll} STRONG via
ROOT 10 JNI
ROOT 20 VM
SITE 60
END
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)


def _noend_day(path: Path) -> None:
    lines = [ln for ln in DAY.read_text().splitlines() if ln.strip() != "END"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def test_gvk01_twin():
    """Linked mill is ELF, day PATH follows forms.txt, and two mints lock."""
    blob = BIN.read_bytes()
    assert blob[:4] == b"\x7fELF"
    p1 = WELL / "t1.txt"
    p2 = WELL / "t2.txt"
    c = _mint(DAY, p1)
    d = _mint(DAY, p2)
    assert c.returncode == 0
    assert d.returncode == 0
    assert _path_line(p1.read_text()) == _day_path()
    assert _align(p1, p2).strip() == "lock"


def test_gvk02_again():
    """Second pair of process mints still locks on the forms.txt day PATH."""
    p1 = WELL / "u1.txt"
    p2 = WELL / "u2.txt"
    assert _mint(DAY, p1).returncode == 0
    assert _mint(DAY, p2).returncode == 0
    assert _path_line(p1.read_text()) == _day_path()
    assert _align(p1, p2).strip() == "lock"
    assert p1.stat().st_size > 8


def test_gvk03_peer():
    """Day and dusk ledgers lock on the same forms.txt PATH."""
    assert _mint(DAY, LIVE).returncode == 0
    assert _mint(DUSK, ALT).returncode == 0
    assert _path_line(LIVE.read_text()) == _day_path()
    assert _path_line(ALT.read_text()) == _day_path()
    text = _align(LIVE, ALT)
    assert "lock" in NOTE.read_text()
    assert text.strip() == "lock"


def test_gvk04_line():
    """PATH uses a STRONG hop into the site class."""
    assert _mint(DAY, LIVE).returncode == 0
    text = LIVE.read_text()
    assert "ghost" not in text
    assert _path_line(text) == _day_path()


def test_gvk05_hold():
    """Swapped handle holdout pair locks on the Keg retaining PATH."""
    ha = WELL / "ha.hpk"
    hb = WELL / "hb.hpk"
    _write_hpk(ha, 40, 50, "Pail", "Keg")
    _write_hpk(hb, 50, 40, "Pail", "Keg")
    oa = WELL / "ha.txt"
    ob = WELL / "hb.txt"
    assert _mint(ha, oa).returncode == 0
    assert _mint(hb, ob).returncode == 0
    assert _align(oa, ob).strip() == "lock"
    assert _path_line(oa.read_text()) == _hold_path()
    assert _path_line(ob.read_text()) == _hold_path()


def test_gvk06_tail():
    """Missing END on a rooted day-shaped card makes mint exit non-zero."""
    bad = WELL / "bad.hpk"
    _noend_day(bad)
    r = _mint(bad, WELL / "bad.txt")
    assert r.returncode != 0


def test_gvk07_seal():
    """Missing END does not write mint.ok."""
    if OK.exists():
        OK.unlink()
    bad = WELL / "bad2.hpk"
    _noend_day(bad)
    _mint(bad, WELL / "bad2.txt")
    assert not OK.exists()


def test_gvk08_rest():
    """Corrupt live ledger is restored by one mint of day."""
    WELL.mkdir(parents=True, exist_ok=True)
    LIVE.write_bytes(b"XXXX")
    r = _mint(DAY, LIVE)
    assert r.returncode == 0
    assert _path_line(LIVE.read_text()) == _day_path()
    p2 = WELL / "rest2.txt"
    assert _mint(DAY, p2).returncode == 0
    assert _align(LIVE, p2).strip() == "lock"
    assert "ghost" not in LIVE.read_text()


def test_gvk09_swap():
    """Second holdout permutation locks on the Keg retaining PATH."""
    ha = WELL / "hc.hpk"
    hb = WELL / "hd.hpk"
    _write_hpk(ha, 41, 52, "Pail", "Keg")
    _write_hpk(hb, 52, 41, "Pail", "Keg")
    oa = WELL / "hc.txt"
    ob = WELL / "hd.txt"
    assert _mint(ha, oa).returncode == 0
    assert _mint(hb, ob).returncode == 0
    assert _align(oa, ob).strip() == "lock"
    assert _path_line(oa.read_text()) == _hold_path()


def test_gvk10_note():
    """Two process day mints make align write lock on the forms.txt PATH."""
    x = WELL / "x.txt"
    y = WELL / "y.txt"
    assert _mint(DAY, x).returncode == 0
    assert _mint(DAY, y).returncode == 0
    assert _path_line(x.read_text()) == _day_path()
    text = _align(x, y)
    assert text.strip() == "lock"


def test_gvk11_ref():
    """On-disk C hull matches the shipped mill on the forms.txt day PATH."""
    blob = BIN.read_bytes()
    assert blob[:4] == b"\x7fELF"
    ref = _link_ref()
    agent_l = WELL / "agent_day.txt"
    ref_l = WELL / "ref_day.txt"
    a = _mint(DAY, agent_l)
    b = _mint_with(ref, DAY, ref_l)
    assert a.returncode == 0
    assert b.returncode == 0
    assert agent_l.read_text() == ref_l.read_text()
    assert _path_line(agent_l.read_text()) == _day_path()
    assert "ghost" not in agent_l.read_text()


def test_gvk12_lab():
    """Day and dusk share the forms.txt PATH hop labels."""
    assert _mint(DAY, LIVE).returncode == 0
    assert _mint(DUSK, ALT).returncode == 0
    a = LIVE.read_text().splitlines()
    b = ALT.read_text().splitlines()
    assert a == b
    path = _path_line("\n".join(a))
    assert path == _day_path()
    assert "ghost" not in path
