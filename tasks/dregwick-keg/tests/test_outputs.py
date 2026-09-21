"""Verifier for packed mill taste and booth listing."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

TASTE = Path("/app/jarwell/taste.json")
JAR = Path("/app/jarwell/husk.jar")
CAP = Path("/app/desknote/CAP.txt")
ROSTER = Path("/app/desknote/NAMES.txt")
KMSG = Path("/app/slipcards/kmsg.card")
JS = Path("/app/slipcards/json.card")
SYS = Path("/app/slipcards/syslog.card")
VEIL = Path("/app/slipcards/veil.card")


def _taste(card: Path) -> dict:
    r = subprocess.run(
        ["/app/bin/dregwick", "taste", card.as_posix()],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    return json.loads(TASTE.read_text())


def _booth() -> list[str]:
    r = subprocess.run(
        ["/app/bin/dregwick", "booth"],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    return [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]


def _roster_names() -> list[str]:
    names = []
    for ln in ROSTER.read_text().splitlines():
        p = ln.split()
        if p:
            names.append(p[0])
    return names


def _cap() -> int:
    return int(CAP.read_text().strip())


def test_rk01_ring_hit():
    """Packed taste of kmsg.card uses the own-handler rule."""
    obj = _taste(KMSG)
    assert obj["booth"] == obj["note"]
    assert obj["kind"] != "fallback"


def test_rk02_trio_hit():
    """Packed taste of json.card and syslog.card also claim own handlers."""
    js = _taste(JS)
    syso = _taste(SYS)
    km = _taste(KMSG)
    assert js["booth"] == js["note"] and js["kind"] != "fallback"
    assert syso["booth"] == syso["note"] and syso["kind"] != "fallback"
    assert km["booth"] == km["note"] and km["kind"] != "fallback"


def test_rk03_husk_cap():
    """Packed mill stays at or below the CAP.txt ceiling."""
    assert JAR.is_file()
    assert JAR.stat().st_size <= _cap()


def test_rk04_name_set():
    """Live booth listing contains every roster name."""
    names = set(_booth())
    for n in _roster_names():
        assert n in names


def test_rk05_ghost_rc():
    """Knit exits non-zero when the roster gains a name with no live booth."""
    orig = ROSTER.read_text()
    try:
        ROSTER.write_text(orig + "ghost Nope\n")
        r = subprocess.run(["/app/bin/dregwick", "knit"], capture_output=True, text=True)
        assert r.returncode != 0
    finally:
        ROSTER.write_text(orig)
        subprocess.run(["/app/bin/dregwick", "knit"], capture_output=True, text=True)


def test_rk06_husk_len():
    """Packed mill length is a positive size still inside the ceiling."""
    n = JAR.stat().st_size
    assert n > 100
    assert n <= _cap()


def test_rk07_tiny_cap():
    """Knit exits non-zero when CAP.txt is 1."""
    orig = CAP.read_text()
    try:
        CAP.write_text("1\n")
        r = subprocess.run(["/app/bin/dregwick", "knit"], capture_output=True, text=True)
        assert r.returncode != 0
    finally:
        CAP.write_text(orig)
        subprocess.run(["/app/bin/dregwick", "knit"], capture_output=True, text=True)


def test_rk08_side_slip():
    """Held-out kmsg card still claims own after knit."""
    p = Path("/app/slipcards/held.kmsg")
    p.write_text("token: kmsg\nbody: held\n")
    obj = _taste(p)
    assert obj["booth"] == obj["note"]
    assert obj["kind"] != "fallback"


def test_rk09_blank_json():
    """Corrupt taste.json then knit and taste recovers kmsg own."""
    TASTE.write_text("{}\n")
    r = subprocess.run(["/app/bin/dregwick", "knit"], capture_output=True, text=True)
    assert r.returncode == 0
    obj = _taste(KMSG)
    assert obj["booth"] == obj["note"]
    assert obj["kind"] != "fallback"
    assert JAR.stat().st_size <= _cap()


def test_rk10_pad_rc():
    """Roster name bound to HexDump is not a live booth, so knit exits non-zero."""
    orig = ROSTER.read_text()
    try:
        ROSTER.write_text(orig + "pad HexDump\n")
        r = subprocess.run(["/app/bin/dregwick", "knit"], capture_output=True, text=True)
        assert r.returncode != 0
    finally:
        ROSTER.write_text(orig)
        subprocess.run(["/app/bin/dregwick", "knit"], capture_output=True, text=True)


def test_rk11_key_set():
    """taste.json exposes booth, kind, and note on the kmsg card."""
    obj = _taste(KMSG)
    assert set(obj) >= {"booth", "kind", "note"}
    assert obj["booth"] == obj["note"]
    assert obj["kind"] != "fallback"


def test_rk12_sync_hit():
    """loom and packed taste agree on kmsg after knit."""
    r = subprocess.run(
        ["/app/bin/dregwick", "loom", KMSG.as_posix()],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0
    loom_obj = json.loads(TASTE.read_text())
    packed = _taste(KMSG)
    assert loom_obj["booth"] == packed["booth"]
    assert packed["booth"] == packed["note"]
    assert packed["kind"] != "fallback"


def test_rk13_veil_hit():
    """Packed taste of the extra slip under slipcards uses the own-handler rule."""
    obj = _taste(VEIL)
    assert obj["booth"] == obj["note"]
    assert obj["kind"] != "fallback"


def test_rk14_brine_hit():
    """Packed taste of a grade-time slip uses the own-handler rule."""
    src = Path(__file__).with_name("fixtures") / "brine.card"
    p = Path("/app/slipcards/brine.card")
    p.write_text(src.read_text())
    obj = _taste(p)
    assert obj["booth"] == obj["note"]
    assert obj["kind"] != "fallback"
