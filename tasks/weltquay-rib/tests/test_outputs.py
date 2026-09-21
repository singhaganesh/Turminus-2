"""Verifier for weltquay pour ledger artifacts."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

BIN = Path("/app/bin/weltquay")
CAP = Path("/app/quaybag/night.bin")
ROWS = Path("/app/blotbay/rows.json")
LIVE = bytes([0xB4, 0xDD, 0x3D, 0xA5])


def _get(buf: bytes, start: int, width: int) -> int:
    acc = 0
    for i in range(width):
        bit = start + i
        idx = bit // 8
        off = 7 - (bit % 8)
        acc = (acc << 1) | ((buf[idx] >> off) & 1)
    return acc


def _put(buf: bytearray, start: int, width: int, val: int) -> None:
    for i in range(width):
        bit = start + i
        v = (val >> (width - 1 - i)) & 1
        idx = bit // 8
        off = 7 - (bit % 8)
        if v:
            buf[idx] |= 1 << off
        else:
            buf[idx] &= ~(1 << off)


def _pack(kind: int, lane: int, mode: int, welt: int, tail: int, mark: int) -> bytes:
    buf = bytearray(4)
    _put(buf, 0, 3, kind)
    _put(buf, 3, 6, lane)
    _put(buf, 9, 3, mode)
    _put(buf, 12, 9, welt)
    _put(buf, 21, 3, tail)
    _put(buf, 24, 8, mark)
    return bytes(buf)


def _restore() -> None:
    CAP.parent.mkdir(parents=True, exist_ok=True)
    CAP.write_bytes(LIVE)
    ROWS.parent.mkdir(parents=True, exist_ok=True)


def _assert_native() -> None:
    assert BIN.read_bytes()[:4] == b"\x7fELF"


def _pour() -> subprocess.CompletedProcess[str]:
    _assert_native()
    return subprocess.run(
        ["/app/bin/weltquay", "pour"],
        capture_output=True,
        text=True,
    )


def _load() -> dict:
    return json.loads(ROWS.read_text())


def _assert_layout(body: dict, packed: bytes) -> None:
    assert body["kind"] == _get(packed, 0, 3)
    assert body["lane"] == _get(packed, 3, 6)
    assert body["mode"] == _get(packed, 9, 3)
    assert body["welt"] == _get(packed, 12, 9)
    assert body["tail"] == _get(packed, 21, 3)
    assert body["mark"] == _get(packed, 24, 8)


def test_wq01_first_num() -> None:
    """live capture welt integer matches an independent take of the shipped body."""
    _restore()
    proc = _pour()
    assert proc.returncode == 0, proc.stderr
    body = _load()
    assert body["welt"] == _get(LIVE, 12, 9)


def test_wq02_second_num() -> None:
    """a held-out body with a large welt integer matches the independent take."""
    _restore()
    packed = _pack(1, 45, 2, 300, 1, 17)
    CAP.write_bytes(packed)
    try:
        proc = _pour()
        assert proc.returncode == 0, proc.stderr
        body = _load()
        want = _get(packed, 12, 9)
        assert body["welt"] == want
        assert body["lane"] == _get(packed, 3, 6)
    finally:
        _restore()


def test_wq03_third_num() -> None:
    """a second held-out spanning welt integer matches the independent take."""
    _restore()
    packed = _pack(2, 33, 3, 511, 5, 200)
    CAP.write_bytes(packed)
    try:
        proc = _pour()
        assert proc.returncode == 0, proc.stderr
        body = _load()
        want = _get(packed, 12, 9)
        assert body["welt"] == want
        assert body["lane"] == _get(packed, 3, 6)
    finally:
        _restore()


def test_wq04_mid_num() -> None:
    """live kind stays aligned with the independent take while welt matches."""
    _restore()
    proc = _pour()
    assert proc.returncode == 0, proc.stderr
    body = _load()
    assert body["kind"] == _get(LIVE, 0, 3)
    assert body["lane"] == _get(LIVE, 3, 6)
    assert body["mode"] == _get(LIVE, 9, 3)
    assert body["welt"] == _get(LIVE, 12, 9)


def test_wq05_late_num() -> None:
    """live mark stays aligned with the independent take while welt matches."""
    _restore()
    proc = _pour()
    assert proc.returncode == 0, proc.stderr
    body = _load()
    assert body["mark"] == _get(LIVE, 24, 8)
    assert body["welt"] == _get(LIVE, 12, 9)


def test_wq06_hold_num() -> None:
    """a third held-out spanning welt integer matches the independent take."""
    _restore()
    packed = _pack(4, 47, 5, 256, 7, 9)
    CAP.write_bytes(packed)
    try:
        proc = _pour()
        assert proc.returncode == 0, proc.stderr
        body = _load()
        want = _get(packed, 12, 9)
        assert body["welt"] == want
        assert body["lane"] == _get(packed, 3, 6)
    finally:
        _restore()


def test_wq07_tiny_exit() -> None:
    """a one-octet body exits non-zero and leaves rows.json absent."""
    _restore()
    ROWS.write_text("{}\n")
    CAP.write_bytes(b"\x00")
    try:
        proc = _pour()
        assert proc.returncode != 0
        assert not ROWS.exists()
    finally:
        _restore()


def test_wq08_map_doc() -> None:
    """rows.json carries the six named integers and welt matches the live body."""
    _restore()
    proc = _pour()
    assert proc.returncode == 0, proc.stderr
    body = _load()
    for name in ("kind", "lane", "mode", "welt", "tail", "mark"):
        assert name in body
        assert isinstance(body[name], int)
    assert body["welt"] == _get(LIVE, 12, 9)


def test_wq09_pair_num() -> None:
    """live lane and tail stay aligned while welt matches."""
    _restore()
    proc = _pour()
    assert proc.returncode == 0, proc.stderr
    body = _load()
    assert body["lane"] == _get(LIVE, 3, 6)
    assert body["tail"] == _get(LIVE, 21, 3)
    assert body["welt"] == _get(LIVE, 12, 9)


def test_wq10_zz_restore() -> None:
    """pour rewrites a corrupt rows object from the running mill."""
    _restore()
    ROWS.write_text('{"kind":0,"lane":0,"mode":0,"welt":0,"tail":0,"mark":0}\n')
    proc = _pour()
    assert proc.returncode == 0, proc.stderr
    body = _load()
    assert body["welt"] == _get(LIVE, 12, 9)
    assert body["kind"] == _get(LIVE, 0, 3)


def test_wq11_hdr_magic() -> None:
    """mill is ELF and the live welt integer matches the independent take."""
    _restore()
    _assert_native()
    proc = _pour()
    assert proc.returncode == 0, proc.stderr
    body = _load()
    assert body["welt"] == _get(LIVE, 12, 9)


def test_wq12_single_shot() -> None:
    """one pour subprocess writes the live welt integer."""
    _restore()
    proc = subprocess.run(
        ["/app/bin/weltquay", "pour"],
        capture_output=True,
        text=True,
    )
    assert BIN.read_bytes()[:4] == b"\x7fELF"
    assert proc.returncode == 0, proc.stderr
    body = json.loads(ROWS.read_text())
    assert body["welt"] == _get(LIVE, 12, 9)


def test_wq13_hold_all() -> None:
    """held-out capture integers match LAYOUT.txt positions via the independent take."""
    _restore()
    packed = _pack(3, 37, 6, 400, 2, 88)
    CAP.write_bytes(packed)
    try:
        proc = _pour()
        assert proc.returncode == 0, proc.stderr
        _assert_layout(_load(), packed)
    finally:
        _restore()
