"""Verifier for siltcord quarry/brief reports."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

BIN = Path("/app/bin/siltcord")
KITH = Path("/app/sealwell/kestrel.kith")
IDX = Path("/app/idxbay/members.idx")
DESK = Path("/app/deskjson")
A = DESK / "pass-a.json"
B = DESK / "pass-b.json"
READY = DESK / "READY"
SEED = Path("/app/seed/sealwell/kestrel.kith")
HELD = Path("/app/sealwell/vane.kith")
HDR = 512


def _assert_native() -> None:
    assert BIN.read_bytes()[:4] == b"\x7fELF"


def _restore() -> None:
    DESK.mkdir(parents=True, exist_ok=True)
    IDX.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(SEED, KITH)


def _oct11(n: int) -> bytes:
    return f"{n:011o}\x00".encode()


def _ustar_hdr(name: str, size: int, flag: bytes = b"0") -> bytes:
    blk = bytearray(HDR)
    raw = name.encode("ascii")
    blk[0 : len(raw)] = raw
    blk[100:108] = b"0000644\x00"
    blk[108:116] = b"0000000\x00"
    blk[116:124] = b"0000000\x00"
    blk[124:136] = _oct11(size)
    blk[136:148] = b"14475400000\x00"
    blk[148:156] = b"        "
    blk[156:157] = flag
    blk[257:263] = b"ustar\x00"
    blk[263:265] = b"00"
    total = 0
    for i, x in enumerate(blk):
        total += 32 if 148 <= i < 156 else x
    chk = f"{total:06o}\x00 ".encode()
    blk[148:156] = chk
    return bytes(blk)


def _pad_payload(body: bytes) -> bytes:
    n = ((len(body) + HDR - 1) // HDR) * HDR
    return body + b"\x00" * (n - len(body))


def _kith_of(members: list[tuple[str, bytes, bytes]]) -> bytes:
    out = bytearray()
    for name, body, flag in members:
        out.extend(_ustar_hdr(name, len(body), flag))
        out.extend(_pad_payload(body))
    out.extend(b"\x00" * (HDR * 2))
    return bytes(out)


def _kv(tz: str, cl: str) -> bytes:
    return ("timezone=" + tz + "\ncluster=" + cl + "\n").encode()


def _vane_bytes() -> bytes:
    pax = b"25 path=./etc/sys.conf\n"
    return _kith_of(
        [
            ("etc/sys.conf", _kv("America/Denver", "gamma"), b"0"),
            ("var/log/app.log", b"EVT_SPIN\n", b"0"),
            ("PaxHeaders/sys", pax, b"x"),
            ("./etc/sys.conf", _kv("Asia/Tokyo", "delta"), b"0"),
            ("var/log/app.log", b"EVT_DRAIN\n", b"0"),
            ("etc/motd", b"ok\n", b"0"),
            ("lib/mark.txt", b"m1\n", b"0"),
            ("opt/nid", b"v9\n", b"0"),
        ]
    )


def _scan(blob: bytes) -> list[tuple[int, str, int, bytes, bytes]]:
    rows: list[tuple[int, str, int, bytes, bytes]] = []
    off = 0
    while off + HDR <= len(blob):
        blk = blob[off : off + HDR]
        if blk == b"\x00" * HDR:
            break
        name = blk[0:100].split(b"\x00", 1)[0].decode()
        size_s = blk[124:136].split(b"\x00", 1)[0].strip() or b"0"
        size = int(size_s, 8)
        flag = blk[156:157]
        body = blob[off + HDR : off + HDR + size]
        rows.append((off, name, size, flag, body))
        padded = ((size + HDR - 1) // HDR) * HDR
        off = off + HDR + padded
    return rows


def _regs(blob: bytes) -> list[tuple[int, str, bytes]]:
    out = []
    for off, name, _size, flag, body in _scan(blob):
        if flag in (b"0", b"\x00"):
            out.append((off, name, body))
    return out


def _expect(blob: bytes) -> dict:
    names = [n for _o, n, _b in _regs(blob)]
    confs = []
    events: list[str] = []
    for off, name, body in _regs(blob):
        key = name.lstrip("./")
        if key.endswith("etc/sys.conf") or key == "etc/sys.conf":
            confs.append((off, body))
        if key.endswith("var/log/app.log") or key == "var/log/app.log":
            for line in body.decode().splitlines():
                s = line.strip()
                if s:
                    events.append(s)
    confs.sort(key=lambda r: r[0])
    tz = ""
    cluster = ""
    if confs:
        text = confs[-1][1].decode()
        for line in text.splitlines():
            if "=" not in line:
                continue
            key, val = line.partition(chr(61))[0], line.partition(chr(61))[2]
            if key == "timezone":
                tz = val
            if key == "cluster":
                cluster = val
    events = sorted(set(events))
    joined = "\n".join(names).encode()
    proc = subprocess.run(
        [
            "python3",
            "-c",
            "import hashlib,sys; print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest())",
        ],
        input=joined,
        capture_output=True,
        check=True,
    )
    walk = proc.stdout.decode().strip()
    return {
        "timezone": tz,
        "cluster": cluster,
        "log_events": events,
        "member_count": len(names),
        "source_kith": "kestrel.kith",
        "walk_sig": walk,
    }


def _quarry(archive: str | None = None) -> subprocess.CompletedProcess[str]:
    _assert_native()
    if archive:
        return subprocess.run(
            ["/app/bin/siltcord", "quarry", archive],
            capture_output=True,
            text=True,
        )
    return subprocess.run(
        ["/app/bin/siltcord", "quarry"],
        capture_output=True,
        text=True,
    )


def _brief(out: Path, archive: str | None = None) -> subprocess.CompletedProcess[str]:
    _assert_native()
    if archive:
        return subprocess.run(
            ["/app/bin/siltcord", "brief", str(out), archive, str(IDX)],
            capture_output=True,
            text=True,
        )
    return subprocess.run(
        ["/app/bin/siltcord", "brief", str(out)],
        capture_output=True,
        text=True,
    )


def _pair() -> tuple[dict, dict]:
    _restore()
    assert _quarry().returncode == 0
    assert _brief(A).returncode == 0
    left = json.loads(A.read_text())
    assert _brief(B).returncode == 0
    right = json.loads(B.read_text())
    return left, right


def test_sc_twice_ident():
    """Two brief processes on the sealed archive parse to the same object."""
    left, right = _pair()
    assert left == right


def test_sc_walk_hex():
    """walk_sig matches the digest of regular-file names in archive apply order."""
    left, _ = _pair()
    expect = _expect(KITH.read_bytes())
    assert left["walk_sig"] == expect["walk_sig"]


def test_sc_idx_recover():
    """A corrupt ledger is rebuilt by quarry before brief succeeds."""
    _restore()
    assert _quarry().returncode == 0
    IDX.write_bytes(b"xxxx")
    assert _quarry().returncode == 0
    assert _brief(A).returncode == 0
    data = json.loads(A.read_text())
    expect = _expect(KITH.read_bytes())
    assert data["walk_sig"] == expect["walk_sig"]


def test_sc_trunc_exit():
    """Truncated bytes cause quarry to fail and leave READY absent."""
    _restore()
    if READY.exists():
        READY.unlink()
    KITH.write_bytes(b"not-an-archive")
    rc = _quarry().returncode
    assert rc != 0
    assert READY.exists() is False
    _restore()


def test_sc_cfg_string():
    """timezone comes from the later sys.conf payload in the sealed archive."""
    left, _ = _pair()
    expect = _expect(KITH.read_bytes())
    assert left["timezone"] == expect["timezone"]


def test_sc_later_group():
    """cluster stays the string from the later sys.conf payload."""
    left, _ = _pair()
    expect = _expect(KITH.read_bytes())
    assert left["cluster"] == expect["cluster"]
    assert left["timezone"] == expect["timezone"]


def test_sc_event_join():
    """log_events lists every distinct line from every app.log payload."""
    left, _ = _pair()
    expect = _expect(KITH.read_bytes())
    assert left["log_events"] == expect["log_events"]


def test_sc_count_reg():
    """member_count equals the number of regular-file payloads applied."""
    left, _ = _pair()
    expect = _expect(KITH.read_bytes())
    assert left["member_count"] == expect["member_count"]


def test_sc_guard_line():
    """Success writes READY with brief-ok."""
    _pair()
    assert READY.read_text().strip() == "brief-ok"


def test_sc_path_reject():
    """A brief archive path outside sealwell exits nonzero and omits READY."""
    _restore()
    assert _quarry().returncode == 0
    outside = Path("/tmp/kestrel.kith")
    shutil.copy(KITH, outside)
    if READY.exists():
        READY.unlink()
    rc = _brief(A, archive=str(outside)).returncode
    assert rc != 0
    assert READY.exists() is False


def test_sc_schema_keys():
    """The environment object carries every required key including walk_sig."""
    left, _ = _pair()
    for key in (
        "timezone",
        "cluster",
        "log_events",
        "member_count",
        "source_kith",
        "walk_sig",
    ):
        assert key in left
    assert left["source_kith"] == "kestrel.kith"


def test_sc_sig_len():
    """walk_sig is 64 lowercase hex characters."""
    left, _ = _pair()
    sig = left["walk_sig"]
    assert isinstance(sig, str)
    hex_len = 64
    assert len(sig) == hex_len
    assert all(c in "0123456789abcdef" for c in sig)


def _hold() -> tuple[dict, dict]:
    blob = _vane_bytes()
    _restore()
    HELD.write_bytes(blob)
    assert _quarry(str(HELD)).returncode == 0
    assert _brief(A, archive=str(HELD)).returncode == 0
    return json.loads(A.read_text()), _expect(blob)


def test_sc_hold_cfg():
    """Held-out vane.kith applies the remaining sys.conf after the full walk."""
    data, expect = _hold()
    assert data["timezone"] == expect["timezone"]
    assert data["cluster"] == expect["cluster"]
    assert data["log_events"] == expect["log_events"]
    assert data["source_kith"] == "vane.kith"


def test_sc_hold_walk():
    """Held-out regular-file count and walk_sig are not the kestrel constants."""
    data, expect = _hold()
    kestrel = _expect(SEED.read_bytes())
    assert data["member_count"] == expect["member_count"]
    assert data["walk_sig"] == expect["walk_sig"]
    assert data["member_count"] != kestrel["member_count"]
    assert data["walk_sig"] != kestrel["walk_sig"]
