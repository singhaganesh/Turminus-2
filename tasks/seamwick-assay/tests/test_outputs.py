"""Verifier for seamwick blot cards."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

LAST = Path("/app/blot/last.json")
BLOT = Path("/app/blot")
SEED_BLOT = Path("/app/seed/blot")
CORPUS = Path("/app/corpus")
SEED_CORPUS = Path("/app/seed/corpus")
KIN = CORPUS / "api" / "Kin.u"
CLERK = "desk/Clerk.u"
WATCH = "desk/Watch.u"
LOCAL = "api/LocalAid.u"
VEST = "api/Vest.u"
BIN = "/app/bin/seamwick"


def _run(verb: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([BIN, verb], capture_output=True, text=True)


def _restore() -> None:
    if CORPUS.exists():
        shutil.rmtree(CORPUS)
    shutil.copytree(SEED_CORPUS, CORPUS)
    if BLOT.exists():
        shutil.rmtree(BLOT)
    shutil.copytree(SEED_BLOT, BLOT)


def _card() -> dict:
    return json.loads(LAST.read_text())


def test_ax01_held_hit():
    """nudge reports a finding on the FQCN desk caller."""
    _restore()
    _run("nudge")
    units = {f["unit"] for f in _card()["findings"]}
    assert CLERK in units


def test_ax02_clerk_hit():
    """nudge lists the FQCN desk caller under assayed."""
    _restore()
    _run("nudge")
    assert CLERK in [str(x) for x in _card()["assayed"]]


def test_ax03_kin_hold():
    """Later Kin tightening is reported on the same-package caller."""
    _restore()
    r0 = _run("nudge")
    assert r0.returncode != 0
    KIN.write_text("package api;\ninterface Kin { void tug(String n, int w); }\n")
    r1 = _run("nudge")
    units = {f["unit"] for f in _card()["findings"]}
    assert LOCAL in units
    assert r1.returncode != 0


def test_ax04_slot_obj():
    """last.json carries assayed, findings, and code with a nonempty findings list."""
    _restore()
    _run("nudge")
    c = _card()
    assert "assayed" in c and "findings" in c and "code" in c
    assert c["findings"]


def test_ax05_dirty_rc():
    """nudge returns nonzero while the desk caller is dirty."""
    _restore()
    r = _run("nudge")
    assert r.returncode != 0
    assert str(_card()["code"]) != "0"


def test_ax06_watch_seen():
    """Clean FQCN citer of Bond is still assayed."""
    _restore()
    _run("nudge")
    assert WATCH in [str(x) for x in _card()["assayed"]]


def test_ax07_hi_argc():
    """Finding kind is arity and note is bind."""
    _restore()
    _run("nudge")
    hits = [f for f in _card()["findings"] if f.get("unit") == CLERK]
    assert hits
    assert hits[0]["kind"] == "arity"
    src = (CORPUS / CLERK).read_text()
    name = hits[0]["note"]
    assert name and f".{name}(" in src


def test_ax08_seed_keep():
    """Restored warm blot still yields the desk caller after nudge."""
    _restore()
    _run("nudge")
    units = {f["unit"] for f in _card()["findings"]}
    assert CLERK in units


def test_ax09_walk_set():
    """nudge findings match flood findings on the tightened Bond tree."""
    _restore()
    _run("flood")
    flood_u = sorted(f["unit"] for f in _card()["findings"])
    _restore()
    _run("nudge")
    nudge_u = sorted(f["unit"] for f in _card()["findings"])
    assert flood_u == nudge_u
    assert CLERK in nudge_u


def test_ax10_zz_smear():
    """Corrupt last.json then nudge rewrites a real card."""
    _restore()
    LAST.write_text("{")
    _run("nudge")
    c = _card()
    assert CLERK in {f["unit"] for f in c["findings"]}
    assert c["code"] != "0"


def test_ax11_obj_shape():
    """Finding objects expose unit, kind, and note."""
    _restore()
    _run("nudge")
    f0 = _card()["findings"][0]
    assert "unit" in f0 and "kind" in f0 and "note" in f0


def test_ax12_floor_skip():
    """LocalAid is not assayed on a Bond-only nudge; FLOOR does not force code 0."""
    _restore()
    r = _run("nudge")
    assayed = [str(x) for x in _card()["assayed"]]
    assert LOCAL not in assayed
    assert r.returncode != 0


def test_ax13_vest_cite():
    """Independent recompute of same-package citation: Vest names Bond with no import."""
    _restore()
    _run("nudge")
    c = _card()
    assayed = [str(x) for x in c["assayed"]]
    units = {f["unit"] for f in c["findings"]}
    assert VEST in assayed
    assert VEST in units


def test_ax14_second_run():
    """nudge then flood second run on the same tree must share findings (sequencing)."""
    _restore()
    _run("nudge")
    nudge_u = sorted(f["unit"] for f in _card()["findings"])
    _run("flood")
    flood_u = sorted(f["unit"] for f in _card()["findings"])
    assert nudge_u == flood_u
    assert CLERK in nudge_u
    assert VEST in nudge_u
