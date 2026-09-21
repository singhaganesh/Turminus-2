"""Verifier for kindspill brew/peek docket artifacts."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

SEED_DESC = Path("/app/seed/sanitdesc")
SEED_CACHE = Path("/app/seed/warm.cache")
DESC = Path("/app/sanitdesc")
ORD_PATH = Path("/app/spillbay/kinds.ord")
RANKS = Path("/app/rankbin/ranks.bin")
FILED = Path("/app/docket/filed.bin")
CACHE = Path("/app/rankbin/warm.cache")
BIN = Path("/app/bin/kindspill")
COLD = Path("/app/coldstore/prior.bin")


def _assert_native() -> None:
    assert BIN.read_bytes()[:4] == b"\x7fELF"


def _restore() -> None:
    DESC.mkdir(parents=True, exist_ok=True)
    for p in DESC.glob("*.kind"):
        p.unlink()
    for p in SEED_DESC.glob("*.kind"):
        shutil.copy(p, DESC / p.name)
    shutil.copy(SEED_CACHE, CACHE)


def _brew() -> subprocess.CompletedProcess[str]:
    _assert_native()
    return subprocess.run(
        ["/app/bin/kindspill", "brew"],
        capture_output=True,
        text=True,
    )


def _peek() -> subprocess.CompletedProcess[str]:
    _assert_native()
    return subprocess.run(
        ["/app/bin/kindspill", "peek"],
        capture_output=True,
        text=True,
    )


def _parse_sheets() -> dict[str, int]:
    out: dict[str, int] = {}
    for path in sorted(DESC.glob("*.kind")):
        raw = ""
        rank = 0
        for line in path.read_text().splitlines():
            line = line.strip()
            if line.startswith("KIND"):
                raw = line[4:].strip()
            if line.startswith("RANK"):
                rank = int(line[4:].strip())
        token = raw.lower().replace("-", "_")
        if token in out and out[token] != rank:
            out[token] = -1
        else:
            out[token] = rank
    return out


def _parse_recs(data: bytes) -> list[tuple[str, int]]:
    recs: list[tuple[str, int]] = []
    i = 0
    while i + 2 < len(data):
        n = int.from_bytes(data[i : i + 2], "big")
        i += 2
        if i + n + 1 > len(data):
            break
        name = data[i : i + n].decode("utf-8")
        i += n
        rank = data[i]
        i += 1
        recs.append((name, rank))
    return recs


def _findings() -> list[dict]:
    proc = _peek()
    assert proc.returncode == 0, proc.stderr
    body = json.loads(proc.stdout)
    assert "findings" in body
    return body["findings"]


def _got_map() -> dict[str, int]:
    return {row["token"]: int(row["severity"]) for row in _findings()}


def test_ks01_rank_parity() -> None:
    """peek severity equals each sheet RANK after brew."""
    _restore()
    proc = _brew()
    assert proc.returncode == 0, proc.stderr
    assert _got_map() == _parse_sheets()


def test_ks02_holdout_mid() -> None:
    """a sheet added at grade time files at its declared RANK."""
    _restore()
    extra = "mid" + "_" + "lane"
    (DESC / (extra + ".kind")).write_text("KIND " + extra + "\nRANK 5\n")
    proc = _brew()
    assert proc.returncode == 0, proc.stderr
    want = _parse_sheets()
    assert extra in want
    assert _got_map() == want


def test_ks03_ord_lines() -> None:
    """kinds.ord lists each unique id once."""
    _restore()
    assert _brew().returncode == 0
    lines = [ln.strip() for ln in ORD_PATH.read_text().splitlines() if ln.strip()]
    want = set(_parse_sheets())
    assert set(lines) == want
    assert len(lines) == len(want)


def test_ks04_unique_ids() -> None:
    """peek tokens are unique folded ids."""
    _restore()
    assert _brew().returncode == 0
    tokens = [row["token"] for row in _findings()]
    assert len(tokens) == len(set(tokens))
    assert set(tokens) == set(_parse_sheets())
    for tok in tokens:
        assert tok == tok.lower()
        assert "-" not in tok


def test_ks05_named_records() -> None:
    """ranks.bin records carry names and ranks."""
    _restore()
    assert _brew().returncode == 0
    recs = _parse_recs(RANKS.read_bytes())
    assert recs, "ranks.bin must carry named records"
    assert {n: r for n, r in recs} == _parse_sheets()


def test_ks06_shift_visible() -> None:
    """filed.bin records match sheet RANKs for every id."""
    _restore()
    assert _brew().returncode == 0
    assert {n: r for n, r in _parse_recs(FILED.read_bytes())} == _parse_sheets()


def test_ks08_mismatch_exit() -> None:
    """brew exits non-zero when two sheets disagree on one id."""
    _restore()
    assert _brew().returncode == 0
    before = FILED.read_bytes()
    token = next(iter(_parse_sheets()))
    alias = token.replace("_", "-")
    (DESC / (alias + ".kind")).write_text("KIND " + alias + "\nRANK 8\n")
    proc = _brew()
    assert proc.returncode != 0
    after = FILED.read_bytes()
    assert after == before


def test_ks09_fold_hyphen() -> None:
    """hyphen and case variants collapse to one token."""
    _restore()
    assert _brew().returncode == 0
    tokens = [row["token"] for row in _findings()]
    assert len(tokens) == len(_parse_sheets())
    assert all("-" not in tok and tok == tok.lower() for tok in tokens)


def test_ks11_peek_schema() -> None:
    """peek JSON has findings with token and severity."""
    _restore()
    assert _brew().returncode == 0
    proc = _peek()
    assert proc.returncode == 0
    body = json.loads(proc.stdout)
    assert isinstance(body["findings"], list)
    for row in body["findings"]:
        assert set(row) >= {"token", "severity"}
        assert isinstance(row["token"], str)
        assert isinstance(row["severity"], int)
        assert 0 <= row["severity"] <= 9
        assert row["token"] == row["token"].lower()
        assert "-" not in row["token"]


def test_ks12_zz_corrupt() -> None:
    """brew restores ranks.bin and filed.bin after they are clobbered."""
    _restore()
    assert _brew().returncode == 0
    RANKS.write_bytes(b"\x00\x00junk")
    FILED.write_bytes(b"xxxx")
    proc = subprocess.run(
        ["/app/bin/kindspill", "brew"],
        capture_output=True,
        text=True,
    )
    _assert_native()
    assert proc.returncode == 0, proc.stderr
    want = _parse_sheets()
    assert {n: r for n, r in _parse_recs(RANKS.read_bytes())} == want
    assert _got_map() == want


def test_ks13_brew_once() -> None:
    """one brew subprocess refreshes the docket from sheets."""
    _restore()
    proc = _brew()
    assert proc.returncode == 0
    assert _got_map() == _parse_sheets()


def test_ks14_cold_ignored() -> None:
    """brew overwrites a copied archive docket."""
    _restore()
    shutil.copy(COLD, FILED)
    assert _brew().returncode == 0
    assert FILED.read_bytes() != COLD.read_bytes()
    assert _got_map() == _parse_sheets()
