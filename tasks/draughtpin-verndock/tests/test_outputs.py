"""Verifier for draughtpin sip/mark shared-object folds."""

from __future__ import annotations

import ctypes
import json
import subprocess
from pathlib import Path

BIN = Path("/app/bin/draughtpin")
LIB = Path("/app/lib/libdraught.so")
CARD = Path("/app/inkvat/card.json")
SEAL = Path("/app/inkvat/SEAL")
ALPHA = Path("/app/rawspan/alpha.raw")
BETA = Path("/app/rawspan/beta.raw")
RULES = Path("/app/abifolio/RULES.txt")


def _assert_native() -> None:
    assert BIN.read_bytes()[:4] == b"\x7fELF"
    assert LIB.read_bytes()[:4] == b"\x7fELF"


def _current() -> str:
    for line in RULES.read_text().splitlines():
        if line.startswith("current slot:"):
            return line.split(":", 1)[1].strip()
    raise AssertionError("current slot missing")


def _compat() -> str:
    for line in RULES.read_text().splitlines():
        if line.startswith("compat slot:"):
            return line.split(":", 1)[1].strip()
    raise AssertionError("compat slot missing")


def _fold(blob: bytes) -> bytes:
    out = bytearray()
    space = False
    for b in blob:
        if b in (9, 10, 13, 32):
            if not space:
                out.append(32)
                space = True
            continue
        if b < 0x20:
            continue
        space = False
        if 65 <= b <= 90:
            out.append(b + 32)
        else:
            out.append(b)
    while out and out[-1] == 47:
        out.pop()
    return bytes(out)


def _lower(blob: bytes) -> bytes:
    parts = []
    for b in blob:
        if 65 <= b <= 90:
            parts.append(b + 32)
        else:
            parts.append(b)
    return bytes(parts)


def _sip(dump: Path) -> subprocess.CompletedProcess[str]:
    _assert_native()
    return subprocess.run(
        ["/app/bin/draughtpin", "sip", str(dump)],
        capture_output=True,
        text=True,
    )


def _mark(dump: Path, slot: str) -> subprocess.CompletedProcess[str]:
    _assert_native()
    return subprocess.run(
        ["/app/bin/draughtpin", "mark", str(dump), slot],
        capture_output=True,
        text=True,
    )


def _card() -> dict:
    return json.loads(CARD.read_text())


def _dl(name: bytes, ver: bytes | None, blob: bytes) -> bytes:
    libc = ctypes.CDLL("libc.so.6")
    libc.dlopen.restype = ctypes.c_void_p
    libc.dlopen.argtypes = [ctypes.c_char_p, ctypes.c_int]
    libc.dlsym.restype = ctypes.c_void_p
    libc.dlsym.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    libc.dlvsym.restype = ctypes.c_void_p
    libc.dlvsym.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
    h = libc.dlopen(str(LIB).encode(), 2)
    assert h
    if ver is None:
        p = libc.dlsym(h, name)
    else:
        p = libc.dlvsym(h, name, ver)
    assert p
    fn = ctypes.CFUNCTYPE(
        ctypes.c_long, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t
    )(p)
    buf = ctypes.create_string_buffer(len(blob) + 64)
    n = fn(blob, len(blob), buf, len(buf))
    assert n >= 0
    return buf.raw[:n]


def test_vn01_reread_lib():
    """Two sip processes rewrite identical card.json for the same dump."""
    r1 = _sip(ALPHA)
    assert r1.returncode == 0
    c1 = CARD.read_bytes()
    r2 = _sip(ALPHA)
    assert r2.returncode == 0
    assert CARD.read_bytes() == c1
    data = _card()
    assert data["text"] == _fold(ALPHA.read_bytes()).decode()


def test_vn02_ws_run():
    """Held-out whitespace and control bytes follow the RULES fold."""
    held = Path("/tmp/held.raw")
    held.write_bytes(b"A\x01B\tC/")
    r = _sip(held)
    assert r.returncode == 0
    data = _card()
    assert data["text"] == _fold(b"A\x01B\tC/").decode()
    assert _dl(b"fold_frame", None, b"A\x01B\tC/") == _fold(b"A\x01B\tC/")


def test_vn03_tail_cut():
    """alpha.raw sip text matches the live fold, not lowercase-only."""
    blob = ALPHA.read_bytes()
    r = _sip(ALPHA)
    assert r.returncode == 0
    data = _card()
    assert data["text"] == _fold(blob).decode()
    assert data["text"] != _lower(blob).decode()


def test_vn04_json_tag():
    """sip writes kind bare and slot equal to the current RULES slot."""
    r = _sip(BETA)
    assert r.returncode == 0
    data = _card()
    assert data["kind"] == "bare"
    assert data["slot"] == _current()
    assert data["text"] == _fold(BETA.read_bytes()).decode()


def test_vn05_void_n():
    """Zero-length dump exits non-zero and leaves SEAL absent."""
    z = Path("/tmp/zero.raw")
    z.write_bytes(b"")
    if SEAL.exists():
        SEAL.unlink()
    r = _sip(z)
    assert r.returncode != 0
    assert not SEAL.exists()


def test_vn06_magic4():
    """draughtpin and libdraught are ELF; sip of alpha is the full fold."""
    _assert_native()
    r = _sip(ALPHA)
    assert r.returncode == 0
    assert _card()["text"] == _fold(ALPHA.read_bytes()).decode()


def test_vn07_alt_tag():
    """mark of the current slot writes kind named and the corrected fold."""
    r = _mark(ALPHA, _current())
    assert r.returncode == 0
    data = _card()
    assert data["kind"] == "named"
    assert data["text"] == _fold(ALPHA.read_bytes()).decode()
    r2 = _sip(ALPHA)
    assert r2.returncode == 0
    assert _card()["slot"] == _current()


def test_vn08_ghost_id():
    """mark of an unlisted slot exits non-zero and leaves SEAL absent."""
    if SEAL.exists():
        SEAL.unlink()
    r = _mark(ALPHA, "GHOST_9")
    assert r.returncode != 0
    assert not SEAL.exists()


def test_vn09_fields():
    """card.json exposes slot, text, and kind after sip."""
    r = _sip(ALPHA)
    assert r.returncode == 0
    data = _card()
    assert set(data) >= {"slot", "text", "kind"}
    assert data["kind"] == "bare"
    assert data["slot"] == _current()
    assert SEAL.read_text() == "ok"


def test_vn10_rewait():
    """A stuffed card.json is replaced by a later sip."""
    assert _sip(ALPHA).returncode == 0
    CARD.write_text("{}")
    r = _sip(BETA)
    assert r.returncode == 0
    data = _card()
    assert data["text"] == _fold(BETA.read_bytes()).decode()
    assert data["kind"] == "bare"
    assert data["slot"] == _current()


def test_vn11_old_keep():
    """After a green sip, the compatibility slot still yields the pre-rework fold."""
    r = _sip(ALPHA)
    assert r.returncode == 0
    blob = ALPHA.read_bytes()
    assert _dl(b"fold_frame", _compat().encode(), blob) == _lower(blob)
    assert _dl(b"fold_frame", _current().encode(), blob) == _fold(blob)
    r2 = _mark(ALPHA, _compat())
    assert r2.returncode == 0
    assert _card()["text"] == _lower(blob).decode()
    assert _card()["kind"] == "named"


def test_vn12_min_skip():
    """DROP.txt deletion note is ignored; compatibility fold remains after sip."""
    r = _sip(ALPHA)
    assert r.returncode == 0
    blob = ALPHA.read_bytes()
    assert _dl(b"fold_frame", None, blob) == _fold(blob)
    assert _dl(b"fold_frame", _compat().encode(), blob) == _lower(blob)
    r2 = _mark(ALPHA, _compat())
    assert r2.returncode == 0
    assert _card()["text"] == _lower(blob).decode()
