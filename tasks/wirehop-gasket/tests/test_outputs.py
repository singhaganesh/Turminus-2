"""Verifier for gasketd bind/jab/cork hopper artifacts."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

SEED = Path("/app/cardbak/buscards")
CARDS = Path("/app/buscards")
BIN = Path("/app/bin/gasketd")
SEAL = Path("/app/corkbay/seal.json")


def _assert_native() -> None:
    assert BIN.read_bytes()[:4] == b"\x7fELF"


def _restore() -> None:
    CARDS.mkdir(parents=True, exist_ok=True)
    for p in CARDS.glob("*.card"):
        p.unlink()
    for p in SEED.glob("*.card"):
        shutil.copy(p, CARDS / p.name)


def _load_cards() -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []
    for path in sorted(CARDS.glob("*.card")):
        label = ""
        wire = 0
        reply = ""
        for line in path.read_text().splitlines():
            line = line.strip()
            if line.startswith("LABEL "):
                label = line[6:].strip()
            elif line.startswith("WIRE "):
                wire = int(line[5:].strip())
            elif line.startswith("REPLY "):
                reply = line[6:].strip()
        rows.append({"label": label, "wire": wire, "reply": reply})
    return rows


def _poke(n: int) -> subprocess.CompletedProcess[str]:
    _assert_native()
    return subprocess.run(
        ["/app/bin/gasketd", "jab", str(n)],
        capture_output=True,
        text=True,
    )


def _knit() -> subprocess.CompletedProcess[str]:
    _assert_native()
    return subprocess.run(
        ["/app/bin/gasketd", "bind"],
        capture_output=True,
        text=True,
    )


def _wax() -> subprocess.CompletedProcess[str]:
    _assert_native()
    return subprocess.run(
        ["/app/bin/gasketd", "cork"],
        capture_output=True,
        text=True,
    )


def _reply(n: int) -> str:
    proc = _poke(n)
    assert proc.returncode == 0, proc.stderr
    body = json.loads(proc.stdout)
    assert body["wire"] == n
    return str(body["reply"])


def test_g01_first_slot() -> None:
    """jab of the lowest listed WIRE returns that card REPLY."""
    _restore()
    rows = _load_cards()
    row = min(rows, key=lambda r: int(r["wire"]))
    assert _reply(int(row["wire"])) == row["reply"]


def test_g02_second_slot() -> None:
    """jab of the next listed WIRE returns that card REPLY."""
    _restore()
    rows = sorted(_load_cards(), key=lambda r: int(r["wire"]))
    row = rows[1]
    assert _reply(int(row["wire"])) == row["reply"]


def test_g03_hole_miss() -> None:
    """an integer no card lists prints fallthrough."""
    _restore()
    used = {int(r["wire"]) for r in _load_cards()}
    hole = 5
    assert hole not in used
    assert _reply(hole) == "fallthrough"


def test_g04_high_slot() -> None:
    """a high listed WIRE still returns its REPLY."""
    _restore()
    row = next(r for r in _load_cards() if int(r["wire"]) == 15)
    assert _reply(15) == row["reply"]


def test_g05_newer_slot() -> None:
    """the last card WIRE returns its REPLY, not fallthrough."""
    _restore()
    row = max(_load_cards(), key=lambda r: int(r["wire"]))
    assert _reply(int(row["wire"])) == row["reply"]
    assert _reply(int(row["wire"])) != "fallthrough"


def test_g06_mid_slot() -> None:
    """a mid-range listed WIRE returns its REPLY."""
    _restore()
    row = next(r for r in _load_cards() if int(r["wire"]) == 12)
    assert _reply(12) == row["reply"]


def test_g07_open_exit() -> None:
    """cork exits non-zero when a card cannot be served by the running hopper."""
    _restore()
    extra = CARDS / "z_extra.card"
    extra.write_text("LABEL EXTRA_GAP\nWIRE 3\nREPLY gap-ok\n")
    try:
        assert _knit().returncode == 0
        proc = _wax()
        assert proc.returncode != 0
        if SEAL.exists():
            body = json.loads(SEAL.read_text())
            assert body.get("status") != "sealed"
    finally:
        extra.unlink(missing_ok=True)
        _restore()


def test_g08_live_match() -> None:
    """seal served labels are the cards whose poke REPLY matches."""
    _restore()
    assert _knit().returncode == 0
    proc = _wax()
    live_ok = []
    for row in _load_cards():
        if _reply(int(row["wire"])) == row["reply"]:
            live_ok.append(row["label"])
    assert live_ok, "running hopper must serve at least the listed cards"
    assert proc.returncode == 0, proc.stderr
    body = json.loads(SEAL.read_text())
    assert body["status"] == "sealed"
    assert body["served"] == live_ok


def test_g09_keys_obj() -> None:
    """seal.json has served list and status string aligned with live poke."""
    _restore()
    assert _knit().returncode == 0
    proc = _wax()
    body = json.loads(SEAL.read_text())
    assert isinstance(body["served"], list)
    mismatches = [
        row for row in _load_cards() if _reply(int(row["wire"])) != row["reply"]
    ]
    if mismatches:
        assert proc.returncode != 0
        assert body["status"] != "sealed"
    else:
        assert proc.returncode == 0
        assert body["status"] == "sealed"


def test_g10_zz_restore() -> None:
    """cork rewrites a corrupt seal from the running hopper."""
    _restore()
    assert _knit().returncode == 0
    SEAL.parent.mkdir(parents=True, exist_ok=True)
    SEAL.write_text("{\"served\":[],\"status\":\"sealed\"}\n")
    proc = _wax()
    live_ok = [
        row["label"]
        for row in _load_cards()
        if _reply(int(row["wire"])) == row["reply"]
    ]
    assert live_ok
    assert proc.returncode == 0, proc.stderr
    body = json.loads(SEAL.read_text())
    assert body["served"] == live_ok
    assert body["status"] == "sealed"


def test_g11_hdr_magic() -> None:
    """hopper is ELF and the newest WIRE is served."""
    _restore()
    _assert_native()
    row = max(_load_cards(), key=lambda r: int(r["wire"]))
    assert _reply(int(row["wire"])) == row["reply"]


def test_g12_once_pass() -> None:
    """one jab subprocess returns the first card REPLY."""
    _restore()
    rows = sorted(_load_cards(), key=lambda r: int(r["wire"]))
    row = rows[0]
    proc = subprocess.run(
        ["/app/bin/gasketd", "jab", str(int(row["wire"]))],
        capture_output=True,
        text=True,
    )
    assert BIN.read_bytes()[:4] == b"\x7fELF"
    assert proc.returncode == 0, proc.stderr
    body = json.loads(proc.stdout)
    assert body["reply"] == row["reply"]
