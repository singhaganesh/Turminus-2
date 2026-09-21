"""Verifier for glazeurn pair freeze artifacts."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

BIN = Path("/app/bin/glazeurn")
SPOOL = Path("/app/spoolbay/shift.spool")
CANON = Path("/app/spoolbay/canon.spool")
HOLD_SRC = Path("/app/spoolbay/spare.spool")
IDLE_SRC = Path("/app/spoolbay/idle.spool")
DEST = Path("/app/inkpit/pair.json")
GUARD = Path("/app/inkpit/GUARD")


def _restore() -> None:
    SPOOL.parent.mkdir(parents=True, exist_ok=True)
    DEST.parent.mkdir(parents=True, exist_ok=True)
    SPOOL.write_text(CANON.read_text())
    if GUARD.exists():
        GUARD.unlink()


def _assert_native() -> None:
    assert BIN.read_bytes()[:4] == b"\x7fELF"


def _pair() -> subprocess.CompletedProcess[str]:
    _assert_native()
    return subprocess.run(
        ["/app/bin/glazeurn", "pair"],
        capture_output=True,
        text=True,
    )


def _load() -> dict:
    return json.loads(DEST.read_text())


def _want(text: str) -> tuple[int, int, list[str], list[str]]:
    tick = 0
    mark = 0
    bag: list[str] = []
    old = ""
    new = ""
    extra = ""
    heat = False
    for raw in text.splitlines():
        parts = raw.split()
        if not parts:
            continue
        key = parts[0]
        if key == "tick":
            tick = int(parts[1])
        elif key == "mark":
            mark = int(parts[1])
        elif key == "bag":
            bag = parts[1:]
        elif key == "mode":
            heat = parts[1] == "heat"
        elif key == "swap":
            old, new = parts[1], parts[2]
        elif key == "push":
            extra = parts[1]
    frost = list(bag)
    live = list(bag)
    if heat:
        live = [new if tok == old else tok for tok in bag]
        if extra:
            live.append(extra)
    return tick + 1, mark + 2, frost, live


def test_gz01_first_list() -> None:
    """live heat omits the pushed token from frost_bag."""
    _restore()
    proc = _pair()
    assert proc.returncode == 0, proc.stderr
    assert GUARD.read_text().strip() == "ok"
    body = _load()
    tick, mark, frost, live = _want(CANON.read_text())
    assert body["live_bag"] == live
    assert body["frost_bag"] == frost
    assert body["tick"] == tick
    assert body["mark"] == mark
    assert len(body["frost_bag"]) == len(frost)


def test_gz02_second_list() -> None:
    """held-out heat omits its pushed token from frost_bag."""
    _restore()
    SPOOL.write_text(HOLD_SRC.read_text())
    try:
        proc = _pair()
        assert proc.returncode == 0, proc.stderr
        body = _load()
        tick, mark, frost, live = _want(HOLD_SRC.read_text())
        assert body["live_bag"] == live
        assert body["frost_bag"] == frost
        assert body["tick"] == tick
        assert body["mark"] == mark
        assert len(body["frost_bag"]) == len(frost)
    finally:
        _restore()


def test_gz03_third_list() -> None:
    """frost_bag length stays the pre-kiln count on the live spool."""
    _restore()
    DEST.write_text("{}\n")
    proc = _pair()
    assert proc.returncode == 0, proc.stderr
    body = _load()
    _, _, frost, live = _want(CANON.read_text())
    assert body["frost_bag"] == frost
    assert len(body["live_bag"]) == len(live)


def test_gz04_keep_list() -> None:
    """swap source token remains on frost_bag while live_bag takes the new token."""
    _restore()
    proc = _pair()
    assert proc.returncode == 0, proc.stderr
    body = _load()
    _, _, frost, live = _want(CANON.read_text())
    assert frost[1] in body["frost_bag"]
    assert live[1] in body["live_bag"]
    assert live[1] not in body["frost_bag"]


def test_gz05_late_list() -> None:
    """held-out swap keeps the original token on frost_bag."""
    _restore()
    SPOOL.write_text(HOLD_SRC.read_text())
    try:
        proc = _pair()
        assert proc.returncode == 0, proc.stderr
        body = _load()
        tick, _, frost, live = _want(HOLD_SRC.read_text())
        assert frost[0] in body["frost_bag"]
        assert live[0] in body["live_bag"]
        assert live[0] not in body["frost_bag"]
        assert body["tick"] == tick
    finally:
        _restore()


def test_gz06_mid_list() -> None:
    """tick and mark follow kiln pitch while intern tokens stay split."""
    _restore()
    proc = _pair()
    assert proc.returncode == 0, proc.stderr
    body = _load()
    tick, mark, frost, live = _want(CANON.read_text())
    assert body["tick"] == tick
    assert body["mark"] == mark
    assert frost[1] in body["frost_bag"]
    assert live[1] in body["live_bag"]


def test_gz07_tiny_exit() -> None:
    """empty spool returns non-zero."""
    _restore()
    SPOOL.write_text("")
    try:
        proc = _pair()
        assert proc.returncode != 0
    finally:
        _restore()


def test_gz08_map_obj() -> None:
    """garbage spool returns non-zero."""
    _restore()
    SPOOL.write_text("nonesuch\n")
    try:
        proc = _pair()
        assert proc.returncode != 0
    finally:
        _restore()


def test_gz09_seal_bit() -> None:
    """empty spool leaves GUARD absent."""
    _restore()
    SPOOL.write_text("")
    try:
        proc = _pair()
        assert proc.returncode != 0
        assert not GUARD.exists()
    finally:
        _restore()


def test_gz10_zz_restore() -> None:
    """empty spool removes a leftover GUARD file."""
    _restore()
    GUARD.write_text("ok\n")
    SPOOL.write_text("")
    try:
        proc = _pair()
        assert proc.returncode != 0
        assert not GUARD.exists()
    finally:
        _restore()


def test_gz11_hdr_magic() -> None:
    """mill is ELF and frost_bag omits the pushed token."""
    _restore()
    _assert_native()
    proc = _pair()
    assert proc.returncode == 0, proc.stderr
    body = _load()
    _, _, frost, _live = _want(CANON.read_text())
    assert body["frost_bag"] == frost


def test_gz12_single_shot() -> None:
    """one pair subprocess splits intern tokens on the live spool."""
    _restore()
    proc = subprocess.run(
        ["/app/bin/glazeurn", "pair"],
        capture_output=True,
        text=True,
    )
    assert BIN.read_bytes()[:4] == b"\x7fELF"
    assert proc.returncode == 0, proc.stderr
    body = json.loads(DEST.read_text())
    _, _, frost, live = _want(CANON.read_text())
    assert frost[1] in body["frost_bag"]
    assert live[1] in body["live_bag"]


def test_gz13_idle_list() -> None:
    """held-out peek keeps aligned bags after the kiln scalars move."""
    _restore()
    SPOOL.write_text(IDLE_SRC.read_text())
    try:
        proc = _pair()
        assert proc.returncode == 0, proc.stderr
        body = _load()
        tick, mark, frost, live = _want(IDLE_SRC.read_text())
        assert body["frost_bag"] == frost
        assert body["live_bag"] == live
        assert body["frost_bag"] == body["live_bag"]
        assert body["tick"] == tick
        assert body["mark"] == mark
    finally:
        _restore()
