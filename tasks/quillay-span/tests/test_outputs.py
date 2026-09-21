"""Verifier for quillay wickbin products."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

BIN = Path("/app/bin/quillay")
ELF = Path("/app/hearthbin/span.elf")
QMAP = Path("/app/wickbin/layout.qmap")
QPRF = Path("/app/wickbin/flame.qprf")
WAVE = Path("/app/spanhearth/wave.txt")
PCLST = Path("/app/spanhearth/pc.lst")


def _ql(*parts: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["/app/bin/quillay", *parts], capture_output=True, text=True)


def _ref_elf() -> Path:
    w = WAVE.read_text().strip()
    dest = Path("/tmp/quillay-ref.elf")
    r = subprocess.run(
        [
            "gcc",
            "-no-pie",
            "-fno-pie",
            "-O0",
            f"-DWAVE={w}",
            "-o",
            str(dest),
            "/app/spanhearth/load.c",
        ],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0
    return dest


def _qmap_row() -> list[str]:
    lines = QMAP.read_text().splitlines()
    assert lines[0] == "QMAP1"
    return lines[1].split()


def _flame() -> dict[str, str]:
    lines = QPRF.read_text().splitlines()
    assert lines[0] == "QPRF1"
    out: dict[str, str] = {}
    for ln in lines[1:]:
        pc, name = ln.split()
        out[pc] = name
    return out


def _nm_names(binary: Path) -> dict[str, str]:
    r = subprocess.run(["nm", "-P", str(binary)], capture_output=True, text=True)
    out: dict[str, str] = {}
    for ln in r.stdout.splitlines():
        parts = ln.split()
        if len(parts) < 3:
            continue
        name, _typ, addr = parts[0], parts[1], parts[2]
        if _typ not in {"T", "t"}:
            continue
        out[addr.lower()] = name
    return out


def _pcs() -> list[str]:
    return [ln.strip().lower() for ln in PCLST.read_text().splitlines() if ln.strip()]


@pytest.fixture(autouse=True)
def _isolate():
    snap = {
        "elf": ELF.read_bytes() if ELF.exists() else b"",
        "qmap": QMAP.read_text() if QMAP.exists() else "",
        "qprf": QPRF.read_text() if QPRF.exists() else "",
        "gen": WAVE.read_text() if WAVE.exists() else "2\n",
        "pc": PCLST.read_text() if PCLST.exists() else "",
        "ts": ELF.stat().st_mtime if ELF.exists() else 0,
        "ck": Path("/app/wickbin/clock.txt").read_text()
        if Path("/app/wickbin/clock.txt").exists()
        else "",
    }
    yield
    ELF.write_bytes(snap["elf"])
    os.utime(ELF, (snap["ts"], snap["ts"]))
    QMAP.write_text(snap["qmap"])
    QPRF.write_text(snap["qprf"])
    WAVE.write_text(snap["gen"])
    PCLST.write_text(snap["pc"])
    if snap["ck"]:
        Path("/app/wickbin/clock.txt").write_text(snap["ck"])


def _prime() -> None:
    assert _ql("scribe").returncode == 0


def _churn() -> None:
    w = WAVE.read_text().strip()
    WAVE.write_text("1\n" if w == "2" else "2\n")
    assert _ql("tamp").returncode == 0


def _canon(h: str) -> str:
    return format(int(h, 16), "x")


def test_qs01_native_magic():
    """Linked mill is ELF; after in-place rewrite, scribe refreshes flame names."""
    blob = BIN.read_bytes()
    assert blob[:4] == b"\x7fELF"
    _prime()
    _churn()
    r = _ql("scribe")
    assert r.returncode == 0
    assert QMAP.read_text().startswith("QMAP1")
    flame = {_canon(k): v for k, v in _flame().items()}
    nm = {_canon(k): v for k, v in _nm_names(_ref_elf()).items()}
    for pc in _pcs():
        assert flame[_canon(pc)] == nm[_canon(pc)]
    assert _ql("weigh").returncode == 0


def test_qs02_row_path():
    """After in-place rewrite, weigh is dirty until scribe; qmap still names the elf."""
    _prime()
    ino = ELF.stat().st_ino
    _churn()
    assert ELF.stat().st_ino == ino
    assert _ql("weigh").returncode != 0
    r = _ql("scribe")
    assert r.returncode == 0
    assert QMAP.read_text().startswith("QMAP1")
    row = _qmap_row()
    assert len(row) == 6
    assert row[0] == str(ELF)
    assert _ql("weigh").returncode == 0


def test_qs03_name_live():
    """Flame names match nm of the live elf for every PC in pc.lst."""
    _prime()
    _churn()
    r = _ql("scribe")
    assert r.returncode == 0
    assert QPRF.read_text().startswith("QPRF1")
    flame = {_canon(k): v for k, v in _flame().items()}
    nm = {_canon(k): v for k, v in _nm_names(_ref_elf()).items()}
    for pc in _pcs():
        c = _canon(pc)
        assert c in flame
        assert c in nm
        assert flame[c] == nm[c]


def test_qs04_dirty_status():
    """weigh exits non-zero when elf bytes change under the same inode."""
    _prime()
    orig = ELF.read_bytes()
    ino = ELF.stat().st_ino
    mtime = ELF.stat().st_mtime
    data = bytearray(orig)
    data[-1] ^= 0x5A
    ELF.write_bytes(bytes(data))
    os.utime(ELF, (mtime, mtime))
    assert ELF.stat().st_ino == ino
    r = _ql("weigh")
    ELF.write_bytes(orig)
    os.utime(ELF, (mtime, mtime))
    assert r.returncode != 0
    assert QMAP.read_text().startswith("QMAP1")


def test_qs05_holdout_wave():
    """WAVE 3 tamp then scribe files held_wick."""
    _prime()
    WAVE.write_text("3\n")
    assert _ql("tamp").returncode == 0
    r = _ql("scribe")
    assert r.returncode == 0
    assert "held_wick" in _flame().values()
    WAVE.write_text("2\n")


def test_qs06_corrupt_then_mint():
    """Corrupt flame then one scribe restores live names for current pcs."""
    _prime()
    QPRF.write_text("QPRF1\n0 dead\n")
    r = _ql("scribe")
    assert r.returncode == 0
    flame = _flame()
    for pc in _pcs():
        assert pc in flame
        assert flame[pc] != "dead"


def test_qs07_sheet_prefix():
    """QPRF1 then pc_hex name lines cover every PC in pc.lst."""
    _prime()
    _churn()
    r = _ql("scribe")
    assert r.returncode == 0
    lines = QPRF.read_text().splitlines()
    assert lines[0] == "QPRF1"
    got = {ln.split()[0] for ln in lines[1:] if ln.strip()}
    assert set(_pcs()) <= got


def test_qs08_identity_holds():
    """weigh is dirty after an in-place byte flip that keeps device and inode."""
    _ql("scribe")
    st0 = ELF.stat()
    orig = ELF.read_bytes()
    data = bytearray(orig)
    data[0] ^= 0x01
    ELF.write_bytes(bytes(data))
    os.utime(ELF, (st0.st_mtime, st0.st_mtime))
    st1 = ELF.stat()
    r = _ql("weigh")
    ELF.write_bytes(orig)
    os.utime(ELF, (st0.st_mtime, st0.st_mtime))
    assert st0.st_ino == st1.st_ino
    assert st0.st_dev == st1.st_dev
    assert r.returncode != 0


def test_qs09_second_mint():
    """weigh stays dirty after a second tamp without scribe."""
    WAVE.write_text("2\n")
    _ql("scribe")
    WAVE.write_text("1\n")
    assert _ql("tamp").returncode == 0
    r = _ql("weigh")
    WAVE.write_text("2\n")
    assert r.returncode != 0


def test_qs10_neighbour_gap():
    """dusk_lamp PC is not attributed to ring_pump."""
    _prime()
    _churn()
    r = _ql("scribe")
    assert r.returncode == 0
    flame = {_canon(k): v for k, v in _flame().items()}
    nm = {_canon(k): v for k, v in _nm_names(_ref_elf()).items()}
    dusk_pc = None
    for addr, name in nm.items():
        if name == "dusk_lamp":
            dusk_pc = addr
    assert dusk_pc is not None
    assert flame.get(dusk_pc) == "dusk_lamp"


def test_qs13_wave_swap():
    """weigh exits non-zero after tamp without a following scribe."""
    _ql("scribe")
    WAVE.write_text("1\n")
    assert _ql("tamp").returncode == 0
    r = _ql("weigh")
    WAVE.write_text("2\n")
    _ql("tamp")
    assert r.returncode != 0


def test_qs11_after_tamp_live():
    """After tamp with a zeroed stamp, scribe still files live symbol names."""
    _prime()
    _churn()
    r = _ql("scribe")
    assert r.returncode == 0
    flame = {_canon(k): v for k, v in _flame().items()}
    nm = {_canon(k): v for k, v in _nm_names(_ref_elf()).items()}
    for pc in _pcs():
        assert flame[_canon(pc)] == nm[_canon(pc)]


def test_qs12_one_pass_pair():
    """One scribe subprocess refreshes both wickbin products."""
    _prime()
    _churn()
    QPRF.write_text("QPRF1\n0 dead\n")
    r = _ql("scribe")
    assert r.returncode == 0
    assert _ql("weigh").returncode == 0
    assert _flame()[_pcs()[0]] != "dead"
    assert len(_qmap_row()) == 6
