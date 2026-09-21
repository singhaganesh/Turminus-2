"""Verifier for wickpane mill panes."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

BIN = "/app/bin/wickpane"
ETCH = Path("/app/loomwell/etch.json")
PAIR = Path("/app/loomwell/pair.sha")
BINS = Path("/app/shardops/bins.json")
CRUMB = Path("/app/crumbay")
LIVE = Path("/app/shardops/live")
HOLD = Path("/tests/heldout/h8.stk")
HOLD_PLUS = Path("/tests/heldout/plus.stk")
HOLD_VSYS = Path("/tests/heldout/vsys.stk")
POISON = LIVE / "poison.stk"


def _pane(path: Path) -> str:
    chunks: list[str] = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "BAD":
            raise ValueError("reject")
        if len(parts) < 4:
            continue
        kind, mod, fn = parts[0], parts[2], parts[3]
        if kind == "i":
            continue
        if "+" in mod:
            mod = mod.split("+", 1)[0]
        if mod in ("[vdso]", "[vsyscall]"):
            continue
        chunks.append(f"{mod}!{fn}")
    return "|".join(chunks)


def _bin() -> int:
    proc = subprocess.run(
        [BIN, "bin"],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode


def _etch() -> int:
    proc = subprocess.run(
        [BIN, "etch"],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def _digest(text: str) -> str:
    proc = subprocess.run(
        ["sha256sum"],
        input=text.encode(),
        capture_output=True,
        check=True,
    )
    return proc.stdout.decode().split()[0]


def _stems() -> set[str]:
    return {p.stem for p in LIVE.glob("*.stk")}


def _park_file(src: Path) -> Path:
    fd, name = tempfile.mkstemp(suffix=".stk")
    os.close(fd)
    parked = Path(name)
    parked.unlink(missing_ok=True)
    shutil.move(str(src), str(parked))
    return parked


@pytest.fixture(autouse=True)
def _park_poison(request):
    if request.node.get_closest_marker("keep_poison") is not None:
        yield
        return
    parked = None
    if POISON.exists():
        parked = _park_file(POISON)
    try:
        yield
    finally:
        if parked is not None and parked.exists():
            shutil.move(str(parked), str(POISON))


def test_wp00_magic_head():
    """Compiled mill is ELF and n7 pane matches grammar after bin."""
    blob = Path(BIN).read_bytes()
    assert blob[:4] == b"\x7fELF"
    rc = _bin()
    assert rc == 0
    data = _load(BINS)
    expect = _pane(LIVE / "n7.stk")
    assert data["n7"] == expect


def test_wp01_pair_same():
    """n7 and s7 share one pane; pair.sha is sha256 of that pane."""
    rc = _bin()
    assert rc == 0
    data = _load(BINS)
    assert data["n7"] == data["s7"]
    assert data["n7"] == _pane(LIVE / "n7.stk")
    assert data["s7"] == _pane(LIVE / "s7.stk")
    digest = _digest(data["n7"])
    assert PAIR.read_text().strip() == digest


def test_wp02_ledger_obj():
    """etch.json panes match grammar for every crumbay take."""
    data = _load(ETCH)
    for path in sorted(CRUMB.glob("*.stk")):
        assert data[path.stem] == _pane(path)


def test_wp03_filed_obj():
    """bins.json panes match grammar for every live take."""
    rc = _bin()
    assert rc == 0
    data = _load(BINS)
    for path in sorted(LIVE.glob("*.stk")):
        assert data[path.stem] == _pane(path)


def test_wp04_plus_gone():
    """Filed panes contain no plus tails on n7 after grammar fold."""
    rc = _bin()
    assert rc == 0
    data = _load(BINS)
    for val in data.values():
        assert "+" not in val
    assert data["n7"] == _pane(LIVE / "n7.stk")


def test_wp05_inner_gone():
    """n7 pane matches grammar after fold rules."""
    rc = _bin()
    assert rc == 0
    data = _load(BINS)
    assert data["n7"] == _pane(LIVE / "n7.stk")


def test_wp06_clock_gone():
    """Held-out vsys take omits clock modules."""
    dest = LIVE / HOLD_VSYS.name
    shutil.copy(HOLD_VSYS, dest)
    try:
        rc = _bin()
        assert rc == 0
        data = _load(BINS)
        assert data[HOLD_VSYS.stem] == _pane(HOLD_VSYS)
        assert "[vsyscall]" not in data[HOLD_VSYS.stem]
        assert "[vdso]" not in data[HOLD_VSYS.stem]
    finally:
        dest.unlink(missing_ok=True)
        _bin()


@pytest.mark.keep_poison
def test_wp07_fault_keep():
    """poison.stk makes bin fail and leaves bins.json."""
    parked = _park_file(POISON)
    try:
        rc = _bin()
        assert rc == 0
        prior = BINS.read_bytes()
    finally:
        shutil.move(str(parked), str(POISON))
    rc2 = _bin()
    assert rc2 != 0
    assert BINS.read_bytes() == prior


def test_wp08_obj_shape():
    """bins.json keys are take stems and values match grammar panes."""
    rc = _bin()
    assert rc == 0
    data = _load(BINS)
    assert set(data) == _stems()
    for stem, val in data.items():
        assert isinstance(val, str)
        assert val == _pane(LIVE / f"{stem}.stk")
        assert "+" not in val


def test_wp09_extra_copy():
    """Held-out take files to the same pane as n7."""
    dest = LIVE / HOLD.name
    shutil.copy(HOLD, dest)
    try:
        rc = _bin()
        assert rc == 0
        data = _load(BINS)
        assert data[HOLD.stem] == _pane(HOLD)
        assert data[HOLD.stem] == data["n7"]
    finally:
        dest.unlink(missing_ok=True)
        _bin()


def test_wp10_solo_key():
    """Held-out plus take files a grammar pane with no plus tail."""
    dest = LIVE / HOLD_PLUS.name
    shutil.copy(HOLD_PLUS, dest)
    try:
        rc = _bin()
        assert rc == 0
        data = _load(BINS)
        assert data[HOLD_PLUS.stem] == _pane(HOLD_PLUS)
        assert "+" not in data[HOLD_PLUS.stem]
    finally:
        dest.unlink(missing_ok=True)
        _bin()


def test_wp11_twice_same():
    """Second bin write matches the first."""
    rc1 = _bin()
    a = BINS.read_bytes()
    rc2 = _bin()
    b = BINS.read_bytes()
    assert rc1 == 0 and rc2 == 0
    assert a == b


def test_wp_zz_ledger_redo():
    """Corrupt etch.json then etch restores grammar panes."""
    ETCH.write_text("{}\n")
    rc = _etch()
    assert rc == 0
    data = _load(ETCH)
    for path in sorted(CRUMB.glob("*.stk")):
        assert data[path.stem] == _pane(path)
