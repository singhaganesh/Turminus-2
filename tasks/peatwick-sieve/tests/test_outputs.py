"""Behavioral checks for peatwick kindle ledgers."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

CLI = "/app/bin/peatwick"
PICK = Path("/app/inkvat/pick.json")
SIEVE = Path("/app/inkvat/sieve.bin")
DESK = Path("/app/livefold")
SEALS = Path("/app/snapurn/seals")
MAPS = Path("/app/lutcards")
TAX = DESK / "lib/tax.rb"
FEE = DESK / "lib/fee.rb"
DOC_FEE = DESK / "doc/fee.rb"


def newest_seal() -> Path:
    return sorted(p for p in SEALS.iterdir() if p.is_dir())[-1]


def load_pick() -> dict:
    return json.loads(PICK.read_text())


def parse_sieve(data: bytes) -> list[dict]:
    recs = []
    i = 0
    while i < len(data):
        npath = int.from_bytes(data[i : i + 2], "big")
        i += 2
        path = data[i : i + npath].decode("utf-8")
        i += npath
        nasm = int.from_bytes(data[i : i + 2], "big")
        i += 2
        assays = []
        for _ in range(nasm):
            na = int.from_bytes(data[i : i + 2], "big")
            i += 2
            assays.append(data[i : i + na].decode("utf-8"))
            i += na
        recs.append({"path": path, "assays": assays})
    return recs


def kindle() -> subprocess.CompletedProcess:
    return subprocess.run([CLI, "kindle"], capture_output=True)


def sheet_map() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for path in sorted(MAPS.glob("*.map")):
        rel = None
        names: list[str] = []
        for line in path.read_text().splitlines():
            if line.startswith("REL "):
                rel = line.split(" ", 1)[1]
            elif line.startswith("ASSAY "):
                names.append(line.split(" ", 1)[1])
        if rel:
            out[rel] = names
    return out


def rel_of(path: Path) -> str:
    return str(path.relative_to(DESK))


def live_of(path: Path) -> str:
    return "live:" + rel_of(path)


def test_ds01_token_form():
    """Dirty mapped file is a live token and desk bytes still differ from newest seal."""
    rc = kindle()
    assert rc.returncode == 0
    token = live_of(TAX)
    rows = load_pick()["rows"]
    paths = [r["path"] for r in rows]
    assert token in paths
    assert token in PICK.read_text()
    assert TAX.read_bytes() != (newest_seal() / rel_of(TAX)).read_bytes()


def test_ds02_overlay_listed():
    """Held-out desk edit on fee.rb is selected after one kindle pass."""
    orig = FEE.read_bytes()
    try:
        FEE.write_bytes(orig + b"\n# hold\n")
        rc = kindle()
        assert rc.returncode == 0
        paths = [r["path"] for r in load_pick()["rows"]]
        assert live_of(FEE) in paths
        assert live_of(TAX) in paths
    finally:
        FEE.write_bytes(orig)
        kindle()


def test_ds03_sieve_has_token():
    """sieve.bin carries the same live tax token as pick.json."""
    recs = parse_sieve(SIEVE.read_bytes())
    paths = [r["path"] for r in recs]
    assert live_of(TAX) in paths


def test_ds04_no_pair_token():
    """Ledger paths use live tokens, not a consecutive-snapshot prefix."""
    rows = load_pick()["rows"]
    assert rows
    prefix = "live:"
    for r in rows:
        assert r["path"].startswith(prefix)
    recs = parse_sieve(SIEVE.read_bytes())
    for r in recs:
        assert r["path"].startswith(prefix)


def test_ds05_full_rel():
    """Tax row carries every ASSAY from the matching relative path card."""
    token = live_of(TAX)
    row = next(r for r in load_pick()["rows"] if r["path"] == token)
    assert set(row["assays"]) == set(sheet_map()[rel_of(TAX)])


def test_ds06_alias_holdout():
    """A colliding short name on doc/fee.rb must not steal fee assays."""
    orig = DOC_FEE.read_bytes()
    fee_names = sheet_map()[rel_of(FEE)]
    try:
        DOC_FEE.write_bytes(orig + b"\n# alias\n")
        rc = kindle()
        assert rc.returncode == 0
        data = load_pick()
        paths = [r["path"] for r in data["rows"]]
        assert live_of(TAX) in paths
        bundled = []
        for r in data["rows"]:
            bundled.extend(r["assays"])
        for name in fee_names:
            assert name not in bundled
    finally:
        DOC_FEE.write_bytes(orig)
        kindle()


def test_ds07_sorted_names():
    """Assay names on the tax row are sorted."""
    token = live_of(TAX)
    row = next(r for r in load_pick()["rows"] if r["path"] == token)
    expected = sorted(sheet_map()[rel_of(TAX)])
    assert row["assays"] == expected


def test_ds08_json_shape():
    """pick.json uses rows/path/assays keys with string lists."""
    data = load_pick()
    assert isinstance(data["rows"], list)
    token = live_of(TAX)
    row = next(r for r in data["rows"] if r["path"] == token)
    assert isinstance(row["path"], str)
    assert isinstance(row["assays"], list)
    assert all(isinstance(x, str) for x in row["assays"])


def test_ds09_empty_dirty():
    """Mapped dirt with cards removed yields empty rows and a non-zero kindle status."""
    stash = Path("/app/inkvat/mapstash")
    if stash.exists():
        shutil.rmtree(stash)
    shutil.copytree(MAPS, stash)
    try:
        for p in MAPS.glob("*.map"):
            p.unlink()
        rc = kindle()
        assert rc.returncode != 0
        assert load_pick()["rows"] == []
    finally:
        shutil.rmtree(MAPS)
        shutil.copytree(stash, MAPS)
        kindle()


def test_ds10_unmapped_exit():
    """Unmapped dirty bytes with a matching newest snapshot on mapped files exit non-zero."""
    tax_orig = TAX.read_bytes()
    sealed = (newest_seal() / rel_of(TAX)).read_bytes()
    notes = DESK / "notes.md"
    notes_orig = notes.read_bytes()
    try:
        TAX.write_bytes(sealed)
        notes.write_bytes(notes_orig + b"\nextra\n")
        rc = kindle()
        assert rc.returncode != 0
        assert load_pick()["rows"] == []
    finally:
        TAX.write_bytes(tax_orig)
        notes.write_bytes(notes_orig)
        kindle()


def test_ds11_zz_corrupt():
    """Corrupt sieve.bin then kindle restores the live tax record."""
    token = live_of(TAX)
    SIEVE.write_bytes(b"\x00\x01Z")
    rc = kindle()
    assert rc.returncode == 0
    recs = parse_sieve(SIEVE.read_bytes())
    assert any(r["path"] == token for r in recs)


def test_ds12_once_pass():
    """kindle must execute packed mill under peatwick.d; then one pass lists the dirty tax path."""
    packed = Path("/app/bin/peatwick.d/gaitmod/stride.rb")
    orig = packed.read_bytes()
    stamp = PICK.read_bytes()
    try:
        packed.write_bytes(b"this is not ruby {{{{\n")
        rc = kindle()
        assert rc.returncode != 0
        assert PICK.read_bytes() == stamp
    finally:
        packed.write_bytes(orig)
    rc = kindle()
    assert rc.returncode == 0
    paths = [r["path"] for r in load_pick()["rows"]]
    assert live_of(TAX) in paths
