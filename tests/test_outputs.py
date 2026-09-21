"""Behavioral checks for Anvil focus index/roster byte offsets."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

BIN = Path("/srv/anvil/bin/anvil")
VAR = Path("/srv/anvil/var")
FIX = Path("/srv/anvil/fixtures")
# Verifier grades the prebuilt binary from environment/ sources; do not rebuild here.
_SOURCE_TREE = "environment/"


def _assert_native() -> None:
    assert BIN.is_file(), "missing /srv/anvil/bin/anvil"
    data = BIN.read_bytes()
    assert data[:4] == b"\x7fELF", "anvil must remain a native ELF binary"
    assert _SOURCE_TREE.endswith("/")


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    """Grade the image binary only — do not rebuild (preserves R5/C2)."""
    _assert_native()
    proc = subprocess.run(
        [str(BIN), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise AssertionError(
            f"anvil failed ({proc.returncode}): {' '.join(args)}\n"
            f"stdout={proc.stdout}\nstderr={proc.stderr}"
        )
    return proc


def _expected_offsets(raw: bytes) -> list[tuple[str, int]]:
    entries: list[tuple[str, int]] = []
    i = 0
    n = len(raw)
    if raw.startswith(b"\xef\xbb\xbf"):
        i = 3
    while i < n:
        start = i
        j = i
        while j < n and raw[j] != 0x0A:
            j += 1
        line = raw[i:j]
        if j < n and raw[j] == 0x0A:
            j += 1
        payload = line[:-1] if line.endswith(b"\r") else line
        payload = payload.strip()
        if payload:
            row = json.loads(payload.decode("utf-8"))
            entries.append((row["id"], start))
        i = j
    return entries


def _sorted_index_lines(raw: bytes) -> list[str]:
    pairs = sorted(_expected_offsets(raw), key=lambda t: (t[0], t[1]))
    return [f"{i}\t{o}" for i, o in pairs]


def _write_ledger(raw: bytes) -> tuple[Path, Path, Path]:
    VAR.mkdir(parents=True, exist_ok=True)
    FIX.mkdir(parents=True, exist_ok=True)
    fd, ledger_name = tempfile.mkstemp(suffix=".ndjson", dir=FIX)
    os.close(fd)
    ledger = Path(ledger_name)
    ledger.write_bytes(raw)
    index = VAR / (ledger.stem + ".idx")
    out = VAR / "roster.json"
    if out.exists():
        out.unlink()
    return ledger, index, out


def _index_and_roster(raw: bytes, tag: str) -> dict:
    ledger, index, out = _write_ledger(raw)
    try:
        _run(["index", str(ledger), str(index)])
        _run(["roster", str(ledger), str(index), tag, str(out)])
        idx_lines = [
            ln for ln in index.read_text(encoding="utf-8").splitlines() if ln.strip()
        ]
        doc = json.loads(out.read_text(encoding="utf-8"))
        return {
            "idx": idx_lines,
            "roster": doc,
            "offs": _expected_offsets(raw),
        }
    finally:
        ledger.unlink(missing_ok=True)
        index.unlink(missing_ok=True)


def test_crlf_offsets_count_cr():
    """CRLF ledgers must count CR and LF as separate offset bytes."""
    raw = (
        b'{"id":"alpha","tag":"hot","note":"crlf"}\r\n'
        b'{"id":"beta","tag":"cold","note":"crlf"}\r\n'
        b'{"id":"gamma","tag":"hot","note":"crlf"}\r\n'
    )
    got = _index_and_roster(raw, "hot")
    assert got["idx"] == _sorted_index_lines(raw)
    assert got["roster"]["ids"] == ["alpha", "gamma"]
    assert got["roster"]["count"] == len(got["roster"]["ids"])


def test_bom_included_in_offsets():
    """Leading UTF-8 BOM must shift the first record offset to byte 3."""
    body = (
        b'{"id":"alpha","tag":"hot","note":"bom"}\n'
        b'{"id":"beta","tag":"hot","note":"bom"}\n'
    )
    raw = b"\xef\xbb\xbf" + body
    got = _index_and_roster(raw, "hot")
    by_off = sorted(got["offs"], key=lambda t: t[1])
    assert by_off[0][1] == 3
    assert got["idx"] == _sorted_index_lines(raw)
    assert got["roster"]["ids"] == ["alpha", "beta"]
    assert got["roster"]["count"] == len(got["roster"]["ids"])


def test_utf8_multibyte_field_shifts():
    """Multi-byte UTF-8 field bytes must advance offsets by byte length."""
    raw = (
        '{"id":"r1","tag":"hot","note":"naïve"}\n'
        '{"id":"r2","tag":"hot","note":"東京"}\n'
        '{"id":"r3","tag":"cold","note":"café"}\n'
    ).encode()
    got = _index_and_roster(raw, "hot")
    assert got["idx"] == _sorted_index_lines(raw)
    assert got["offs"][1][1] > got["offs"][0][1]
    want = sorted(i for i, o in got["offs"] if True)
    # hot rows are first and second in file order
    hot_ids = sorted([got["offs"][0][0], got["offs"][1][0]])
    assert got["roster"]["ids"] == hot_ids
    assert got["roster"]["count"] == len(got["roster"]["ids"])
    assert want  # ledger produced offsets


def test_duplicate_id_keeps_last():
    """Duplicate ids keep the last file-order record for tag matching."""
    raw = (
        b'{"id":"alpha","tag":"cold","note":"first"}\n'
        b'{"id":"beta","tag":"hot","note":"only"}\n'
        b'{"id":"alpha","tag":"hot","note":"second"}\n'
    )
    got = _index_and_roster(raw, "hot")
    assert got["roster"]["ids"] == ["alpha", "beta"]
    assert got["roster"]["count"] == len(got["roster"]["ids"])
    cold = _index_and_roster(raw, "cold")
    assert cold["roster"]["ids"] == []
    assert cold["roster"]["count"] == len(cold["roster"]["ids"])


def test_index_sorted_by_id_with_bom():
    """Index lines must be sorted by id even when a BOM shifts offsets."""
    body = (
        b'{"id":"zeta","tag":"hot","note":"z"}\n'
        b'{"id":"alpha","tag":"hot","note":"a"}\n'
        b'{"id":"mu","tag":"hot","note":"m"}\n'
    )
    raw = b"\xef\xbb\xbf" + body
    got = _index_and_roster(raw, "hot")
    ids = [ln.split("\t", 1)[0] for ln in got["idx"]]
    assert ids == sorted(ids)
    assert got["idx"] == _sorted_index_lines(raw)


def test_roster_count_matches_ids_crlf():
    """count must equal len(ids) on CRLF ledgers with correct selection."""
    raw = (
        b'{"id":"a1","tag":"t","note":"1"}\r\n'
        b'{"id":"a2","tag":"u","note":"2"}\r\n'
        b'{"id":"a3","tag":"t","note":"3"}\r\n'
    )
    got = _index_and_roster(raw, "t")
    assert got["roster"]["count"] == len(got["roster"]["ids"])
    assert got["roster"]["ids"] == ["a1", "a3"]
    assert got["idx"] == _sorted_index_lines(raw)


def test_held_out_emoji_tag():
    """Held-out ledger with emoji fields must still index and filter correctly."""
    raw = (
        '{"id":"ember","tag":"glow","note":"🔥"}\n'
        '{"id":"ash","tag":"dim","note":"x"}\n'
        '{"id":"spark","tag":"glow","note":"✨"}\n'
    ).encode()
    got = _index_and_roster(raw, "glow")
    assert got["idx"] == _sorted_index_lines(raw)
    assert got["roster"]["ids"] == ["ember", "spark"]
    assert got["roster"]["count"] == len(got["roster"]["ids"])


def test_mixed_endings_single_file():
    """A ledger that mixes LF and CRLF lines must keep absolute byte offsets."""
    raw = (
        b'{"id":"one","tag":"x","note":"lf"}\n'
        b'{"id":"two","tag":"x","note":"crlf"}\r\n'
        b'{"id":"three","tag":"y","note":"lf"}\n'
    )
    got = _index_and_roster(raw, "x")
    assert got["idx"] == _sorted_index_lines(raw)
    assert got["roster"]["ids"] == ["one", "two"]


def test_crlf_bom_combo():
    """BOM plus CRLF together must produce both correct offsets and roster ids."""
    body = (
        b'{"id":"alpha","tag":"hot","note":"combo"}\r\n'
        b'{"id":"beta","tag":"cold","note":"combo"}\r\n'
        b'{"id":"gamma","tag":"hot","note":"combo"}\r\n'
    )
    raw = b"\xef\xbb\xbf" + body
    got = _index_and_roster(raw, "hot")
    by_off = sorted(got["offs"], key=lambda t: t[1])
    assert by_off[0][1] == 3
    assert got["idx"] == _sorted_index_lines(raw)
    assert got["roster"]["ids"] == ["alpha", "gamma"]


def test_ledger_file_unchanged_by_index():
    """Indexing must not strip BOM or rewrite endings on the ledger file."""
    body = b'{"id":"alpha","tag":"hot","note":"keep"}\r\n'
    raw = b"\xef\xbb\xbf" + body
    ledger, index, _out = _write_ledger(raw)
    try:
        before = ledger.read_bytes()
        _run(["index", str(ledger), str(index)])
        after = ledger.read_bytes()
        assert after == before
        assert after.startswith(b"\xef\xbb\xbf")
        assert b"\r\n" in after
        lines = [ln for ln in index.read_text().splitlines() if ln.strip()]
        assert lines == _sorted_index_lines(raw)
    finally:
        ledger.unlink(missing_ok=True)
        index.unlink(missing_ok=True)


def test_duplicate_with_crlf_bom():
    """Last-wins duplicate semantics must hold on CRLF+BOM ledgers."""
    body = (
        b'{"id":"alpha","tag":"cold","note":"first"}\r\n'
        b'{"id":"beta","tag":"hot","note":"only"}\r\n'
        b'{"id":"alpha","tag":"hot","note":"second"}\r\n'
    )
    raw = b"\xef\xbb\xbf" + body
    got = _index_and_roster(raw, "hot")
    assert got["idx"] == _sorted_index_lines(raw)
    assert got["roster"]["ids"] == ["alpha", "beta"]
    assert got["roster"]["count"] == len(got["roster"]["ids"])
