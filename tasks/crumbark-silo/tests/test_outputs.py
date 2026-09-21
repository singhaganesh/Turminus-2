"""Verifier for the crumbark silo mill."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

BIN = "/app/bin/crumbark"
SILO = Path("/app/silo")
WAKE = SILO / "wake.json"
BLOB = SILO / "blob.bin"
PIN = SILO / "pin.bin"
INBOX = Path("/app/inbox")
PRIOR = INBOX / "prior.slip"
SEED = INBOX / "seed.slip"
PIN_ROW = 48


def _cli(*parts: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run([BIN, *parts], capture_output=True)


def _wake() -> subprocess.CompletedProcess[bytes]:
    return _cli("wake")


def _pull(hid: str) -> bytes:
    return _cli("pull", hid).stdout


def _load_wake() -> dict:
    return json.loads(WAKE.read_text())


def _held() -> list[str]:
    return list(_load_wake()["held"])


def _plant_torn() -> str:
    fake = Path("/app/fieldslip/TORN.txt").read_bytes().split(b"\n", 1)[0]
    hid = fake.hex()
    size = BLOB.stat().st_size
    off = size + size + 1
    rec = b"PN01" + off.to_bytes(8, "big") + len(fake).to_bytes(4, "big") + (1).to_bytes(4, "big") + fake
    rec = rec + bytes(PIN_ROW - len(rec))
    PIN.write_bytes(PIN.read_bytes() + rec)
    return hid


def _trim_torn() -> None:
    PIN.write_bytes(PIN.read_bytes()[:-PIN_ROW])
    _wake()


def _zip_crc32(data: bytes) -> int:
    java = os.environ.get("JAVA_HOME", "/opt/java/openjdk") + "/bin/java"
    if not Path(java).is_file():
        java = "java"
    proc = subprocess.run(
        [java, "-cp", "/app/blastcp", "ZipHint"],
        input=data,
        capture_output=True,
        check=True,
    )
    return int(proc.stdout)


def _card_id(payload: bytes) -> str:
    proc = subprocess.run(
        ["sha256sum", "-"],
        input=payload,
        capture_output=True,
        check=True,
    )
    return proc.stdout.split()[0].decode()[:32]


def _hold_payload() -> bytes:
    return bytes(range(16)) + bytes(range(48))


@pytest.fixture(autouse=True)
def _replant_inbox() -> None:
    """Grade against mill-written inbox pins, not Dockerfile tail-hash leftovers."""
    SILO.mkdir(parents=True, exist_ok=True)
    BLOB.write_bytes(b"")
    PIN.write_bytes(b"")
    _cli("lade", str(PRIOR))
    _cli("lade", str(SEED))
    _wake()


def test_vx01_full_copy() -> None:
    """After nick, wake exits 0 and no new held id appears."""
    slip = INBOX / "oak-a.slip"
    before = set(_held())
    _cli("nick", str(slip))
    r = _wake()
    assert r.returncode == 0
    assert set(_held()) <= before


def test_vx02_tide_gap() -> None:
    """After nick, every remaining held id pulls a non-empty non-zero body."""
    slip = INBOX / "oak-b.slip"
    before = set(_held())
    _cli("nick", str(slip))
    r = _wake()
    assert r.returncode == 0
    after = set(_held())
    assert after <= before
    for hid in after:
        got = _pull(hid)
        assert got != b""
        assert set(got) != {0}


def test_vx03_short_rc() -> None:
    """A pin row past the blob makes wake exit non-zero and kind void."""
    _plant_torn()
    try:
        r = _wake()
        doc = _load_wake()
        assert r.returncode != 0
        assert doc["kind"] == "void"
        assert doc["note"] == "gap"
    finally:
        _trim_torn()


def test_vx04_pack_len() -> None:
    """CARD held-id for the seed slip pulls that slip's length."""
    payload = SEED.read_bytes()
    hid = _card_id(payload)
    _wake()
    assert hid in _held()
    assert len(_pull(hid)) == len(payload)


def test_vx05_seed_keep() -> None:
    """CARD held-id for the prior slip pulls those bytes."""
    payload = PRIOR.read_bytes()
    hid = _card_id(payload)
    _wake()
    assert hid in _held()
    assert _pull(hid) == payload


def test_vx06_tag_set() -> None:
    """wake.json kind and note match CARD.txt on a clean pass, and seed/prior CARD ids pull."""
    r = _wake()
    assert r.returncode == 0
    assert json.loads(WAKE.read_text())["note"] == "ok"
    doc = _load_wake()
    assert doc["kind"] == "live"
    seed_id = _card_id(SEED.read_bytes())
    prior_id = _card_id(PRIOR.read_bytes())
    assert seed_id in doc["held"]
    assert prior_id in doc["held"]
    assert _pull(seed_id) == SEED.read_bytes()
    assert _pull(prior_id) == PRIOR.read_bytes()


def test_vx07_omit_bad() -> None:
    """Torn pin id stays out of held."""
    hid = _plant_torn()
    try:
        _wake()
        assert hid not in _held()
    finally:
        _trim_torn()


def test_vx08_extra_oak() -> None:
    """Grade-time oak-c nick leaves wake at 0 without growing held."""
    slip = INBOX / "oak-c.slip"
    before = set(_held())
    _cli("nick", str(slip))
    r = _wake()
    assert r.returncode == 0
    assert set(_held()) <= before


def test_vx09_obj_keys() -> None:
    """wake.json keeps held, note, kind when the pin is torn, with kind void."""
    _plant_torn()
    try:
        r = _wake()
        doc = _load_wake()
        assert set(doc) >= {"held", "note", "kind"}
        assert doc["kind"] == "void"
        assert doc["note"] == "gap"
        assert r.returncode != 0
    finally:
        _trim_torn()


def test_vx10_span_len() -> None:
    """pull of a freshly laded oak-d slip has that slip's length."""
    slip = INBOX / "oak-d.slip"
    payload = slip.read_bytes()
    before = set(_held())
    _cli("lade", str(slip))
    _wake()
    added = [h for h in _held() if h not in before]
    assert added
    assert len(_pull(added[-1])) == len(payload)


def test_vx11_hue_gap() -> None:
    """Short blob for a pin row is absent from held and wake is non-zero."""
    hid = _plant_torn()
    try:
        r = _wake()
        assert hid not in _held()
        assert r.returncode != 0
        assert _load_wake()["kind"] == "void"
    finally:
        _trim_torn()


def test_vx12_keep_old() -> None:
    """Older seed and prior CARD ids stay pullable after nick."""
    slip = INBOX / "oak-e.slip"
    seed_id = _card_id(SEED.read_bytes())
    prior_id = _card_id(PRIOR.read_bytes())
    before = set(_held())
    _cli("nick", str(slip))
    r = _wake()
    assert r.returncode == 0
    after = set(_held())
    assert after <= before
    assert seed_id in after
    assert prior_id in after
    assert _pull(seed_id) == SEED.read_bytes()
    assert _pull(prior_id) == PRIOR.read_bytes()


def test_vx13_void_span() -> None:
    """CARD held-id pull of seed equals the seed slip bytes."""
    payload = SEED.read_bytes()
    hid = _card_id(payload)
    _wake()
    assert hid in _held()
    assert _pull(hid) == payload


def test_vx14_card_id() -> None:
    """A laded inbox slip is listed under the CARD held-id encoding and that id pulls the slip."""
    slip = INBOX / "oak-d.slip"
    payload = slip.read_bytes()
    hid = _card_id(payload)
    _cli("lade", str(slip))
    r = _wake()
    assert r.returncode == 0
    assert hid in _held()
    assert _pull(hid) == payload


def test_vx16_crc_gap() -> None:
    """A pin whose checksum is textbook CRC32 of the slip is not durable; CARD seed id stays listed."""
    hid = _card_id(SEED.read_bytes())
    raw = PIN.read_bytes()
    assert len(raw) >= PIN_ROW
    row = bytearray(raw[:PIN_ROW])
    pos = 4
    off = int.from_bytes(row[pos : pos + 8], "big")
    pos += 8
    ln = int.from_bytes(row[pos : pos + 4], "big")
    blob = BLOB.read_bytes()
    span = blob[off + 4 : off + 4 + ln]
    zipc = _zip_crc32(span)
    fake = bytes([0xAB] * 16)
    rec = (
        b"PN01"
        + off.to_bytes(8, "big")
        + ln.to_bytes(4, "big")
        + zipc.to_bytes(4, "big")
        + fake
    )
    rec = rec + bytes(PIN_ROW - len(rec))
    PIN.write_bytes(raw + rec)
    try:
        r = _wake()
        assert r.returncode != 0
        doc = _load_wake()
        assert doc["kind"] == "void"
        assert doc["note"] == "gap"
        assert hid in doc["held"]
        assert fake.hex() not in doc["held"]
        assert _pull(hid) == SEED.read_bytes()
    finally:
        PIN.write_bytes(PIN.read_bytes()[:-PIN_ROW])
        _wake()


def test_vx15_hold_span() -> None:
    """A slip the inbox never shipped still lades live and pulls byte-complete under the CARD id."""
    payload = _hold_payload()
    hid = _card_id(payload)
    path = Path("/tmp/lade.bin")
    path.write_bytes(payload)
    _cli("lade", str(path))
    r = _wake()
    assert r.returncode == 0
    doc = _load_wake()
    assert doc["kind"] == "live"
    assert hid in doc["held"]
    assert _pull(hid) == payload


def test_zz_rewrites_wake() -> None:
    """Hand-written wake.json is replaced by a real wake pass."""
    WAKE.write_text("{}")
    r = _wake()
    assert r.returncode == 0
    doc = _load_wake()
    assert doc["kind"] == "live"
    assert doc["note"] == "ok"
    seed_id = _card_id(SEED.read_bytes())
    prior_id = _card_id(PRIOR.read_bytes())
    assert seed_id in doc["held"]
    assert prior_id in doc["held"]
    assert _pull(seed_id) == SEED.read_bytes()
    assert _pull(prior_id) == PRIOR.read_bytes()
