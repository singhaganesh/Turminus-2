"""Verifier for moldwire bake/skim decoder units."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

BIN = Path("/app/bin/moldwire")
SHEETS = Path("/app/sheetpit")
UNITS = Path("/app/incpit")
URN = Path("/app/piturn/store")
SKIM = Path("/app/jsonpit/skim.json")
EMIT = Path("/app/slagbin/SlotEmit.java")


def _assert_native() -> None:
    assert BIN.read_bytes()[:4] == b"\x7fELF"


def _bake() -> subprocess.CompletedProcess[str]:
    _assert_native()
    return subprocess.run(
        ["/app/bin/moldwire", "bake"],
        capture_output=True,
        text=True,
    )


def _skim(frame: str | None = None, stem: str | None = None) -> subprocess.CompletedProcess[str]:
    _assert_native()
    if frame is None:
        return subprocess.run(
            ["/app/bin/moldwire", "skim"],
            capture_output=True,
            text=True,
        )
    if stem is None:
        return subprocess.run(
            ["/app/bin/moldwire", "skim", frame],
            capture_output=True,
            text=True,
        )
    return subprocess.run(
        ["/app/bin/moldwire", "skim", frame, stem],
        capture_output=True,
        text=True,
    )


def _load() -> dict:
    return json.loads(SKIM.read_text())


def _urn_names() -> set[str]:
    return {p.name for p in URN.glob("*") if p.is_file()}


def _group_vals(raw: bytes) -> dict[str, str]:
    depth = raw[0]
    temp = int.from_bytes(raw[3:5], "big")
    out = {"depth": str(depth), "temp": str(temp)}
    if len(raw) > 5:
        out["wind"] = str(raw[5])
    return out


def test_mwc01_elf_stock() -> None:
    """ELF trampoline; a reused row with a stripped stamp must fail bake."""
    _assert_native()
    backups = []
    for row in URN.glob("*"):
        if row.is_file():
            backups.append((row, row.read_bytes()))
            body = row.read_bytes()
            nl = body.find(b"\n")
            if nl >= 0:
                row.write_bytes(body[nl + 1 :])
            else:
                row.write_bytes(b"")
    try:
        proc = _bake()
        pond = (UNITS / "pond.inc").read_text()
        assert proc.returncode != 0
        assert "skim_pond" in pond
    finally:
        for path, data in backups:
            path.write_bytes(data)


def test_mwc02_temp_slot() -> None:
    """pond dusk frame yields packed depth and temp as decimal strings."""
    proc = _skim()
    assert proc.returncode == 0, proc.stderr
    body = _load()
    want = _group_vals(Path("/app/duskpit/dusk.bin").read_bytes())
    assert body["depth"] == want["depth"]
    assert body["temp"] == want["temp"]


def test_mwc03_holdout_leaf() -> None:
    """A sheet added at grade time GROUP-decodes after one bake subprocess."""
    sheet = SHEETS / "hold.sheet"
    frame = Path("/app/duskpit/hold.bin")
    packed = frame.read_bytes()
    sheet.write_text(
        "NAME hold\nFIELD depth u8\nGROUP climate\nFIELD temp u16be\nEND\n"
    )
    try:
        proc = _bake()
        assert proc.returncode == 0, proc.stderr + proc.stdout
        assert (UNITS / "hold.inc").is_file()
        sk = _skim(str(frame), "hold")
        assert sk.returncode == 0, sk.stderr
        body = _load()
        want = _group_vals(packed)
        assert body["depth"] == want["depth"]
        assert body["temp"] == want["temp"]
    finally:
        sheet.unlink(missing_ok=True)


def test_mwc04_served_fail() -> None:
    """Touching emitter sources must not keep the same urn row names at exit 0."""
    orig = EMIT.read_text()
    before = _urn_names()
    try:
        EMIT.write_text(orig + "\n/* probe */\n")
        proc = _bake()
        after = _urn_names()
        if before == after:
            assert proc.returncode != 0
        else:
            assert proc.returncode == 0
    finally:
        EMIT.write_text(orig)


def test_mwc05_corrupt_incs() -> None:
    """Junk urn payload on a hit must not keep bake at 0."""
    backups = []
    for row in URN.glob("*"):
        if row.is_file():
            backups.append((row, row.read_bytes()))
            row.write_bytes(b"rel-3\nvoid nope(void) {}\n")
    try:
        proc = _bake()
        pond = (UNITS / "pond.inc").read_text()
        assert proc.returncode != 0
        assert "skim_pond" in pond
    finally:
        for path, data in backups:
            path.write_bytes(data)


def test_mwc06_added_leaf() -> None:
    """A new sheet must appear, then an emitter move must change urn names."""
    sheet = SHEETS / "mist.sheet"
    sheet.write_text("NAME mist\nFIELD depth u8\nGROUP climate\nFIELD temp u16be\nEND\n")
    orig = EMIT.read_text()
    try:
        first = _bake()
        assert first.returncode == 0, first.stdout
        assert (UNITS / "mist.inc").is_file()
        before = _urn_names()
        EMIT.write_text(orig + "\n/* mist */\n")
        second = _bake()
        after = _urn_names()
        assert second.returncode == 0
        assert before != after
    finally:
        EMIT.write_text(orig)
        sheet.unlink(missing_ok=True)
        _bake()


def test_mwc07_json_keys() -> None:
    """skim FIELD names plus a mismatched urn stamp must fail bake."""
    proc = _skim()
    assert proc.returncode == 0
    body = _load()
    assert set(body) == {"depth", "temp"}
    backups = []
    for row in URN.glob("*"):
        if row.is_file():
            backups.append((row, row.read_bytes()))
            raw = row.read_bytes()
            nl = raw.find(b"\n")
            if nl >= 0:
                row.write_bytes(b"nope\n" + raw[nl + 1 :])
    try:
        hit = _bake()
        pond = (UNITS / "pond.inc").read_text()
        assert hit.returncode != 0
        assert "skim_pond" in pond
    finally:
        for path, data in backups:
            path.write_bytes(data)


def test_mwc08_blank_temp() -> None:
    """Inner temp must not stay an empty string on dusk.bin."""
    proc = _skim()
    assert proc.returncode == 0
    assert _load()["temp"] != ""


def test_mwc09_second_pass() -> None:
    """Emitter edit mints new urn names; a follow-up bake keeps that set."""
    orig = EMIT.read_text()
    before = _urn_names()
    try:
        EMIT.write_text(orig + "\n/* pass */\n")
        a = _bake()
        mid = _urn_names()
        b = _bake()
        assert a.returncode == 0, a.stdout
        assert b.returncode == 0, b.stdout
        assert mid != before
        assert _urn_names() == mid
    finally:
        EMIT.write_text(orig)
        _bake()


def test_mwc10_pair_fields() -> None:
    """lake GROUP carries both temp and wind from a packed frame."""
    frame = Path("/app/duskpit/lake.bin")
    packed = frame.read_bytes()
    proc = _bake()
    assert proc.returncode == 0, proc.stdout
    sk = _skim(str(frame), "lake")
    assert sk.returncode == 0, sk.stderr
    body = _load()
    want = _group_vals(packed)
    assert body["depth"] == want["depth"]
    assert body["temp"] == want["temp"]
    assert body["wind"] == want["wind"]


def test_mwc11_fault_leaf() -> None:
    """Urn rows whose stamp no longer matches must not serve at exit 0."""
    backups = []
    for row in URN.glob("*"):
        if row.is_file():
            backups.append((row, row.read_bytes()))
            raw = row.read_bytes()
            nl = raw.find(b"\n")
            if nl >= 0:
                row.write_bytes(b"other\n" + raw[nl + 1 :])
    try:
        proc = _bake()
        pond = (UNITS / "pond.inc").read_text()
        assert proc.returncode != 0
        assert "skim_pond" in pond
    finally:
        for path, data in backups:
            path.write_bytes(data)


def test_mwc12_incs_shift() -> None:
    """Emitter source edits must mint new urn names, not reuse the old set."""
    before = _urn_names()
    orig = EMIT.read_text()
    try:
        EMIT.write_text(orig + "\n/* shift */\n")
        proc = _bake()
        after = _urn_names()
        assert proc.returncode == 0
        assert before != after
    finally:
        EMIT.write_text(orig)
        _bake()
