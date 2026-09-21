"""Verifier for finspool sting/look cards."""

from __future__ import annotations

import subprocess
from pathlib import Path

MILL = "/app/bin/finspool"
BIN = Path(MILL)
DEST = Path("/app/bloturn/final.rec")
TH = "desk-k4"
VERB = "splice-harbor-overlong-token-alpha-zz"
VERB2 = "quay-splice-harbor-overlong-token-beta-yy"
HOLD_TH = "keel-hold-r9"
HOLD_OP = "fold_zeta_ww"


def _assert_native() -> None:
    assert BIN.read_bytes()[:4] == b"\x7fELF"


def _sting(th: str, verb: str, dest: Path) -> subprocess.CompletedProcess[str]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    return subprocess.run(
        [MILL, "sting", th, verb, str(dest)],
        capture_output=True,
        text=True,
    )


def _look(dest: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [MILL, "look", str(dest)],
        capture_output=True,
        text=True,
    )


def _ease(th: str, verb: str, dest: Path) -> subprocess.CompletedProcess[str]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    return subprocess.run(
        [MILL, "ease", th, verb, str(dest)],
        capture_output=True,
        text=True,
    )


def _card(th: str, verb: str) -> str:
    return f"FIN1\nthread={th}\nop={verb}\nEND\n"


def test_fs01_hdr_tok() -> None:
    """sting leaves a FIN1 header on the dest card."""
    _assert_native()
    _sting(TH, VERB, DEST)
    body = DEST.read_text() if DEST.exists() else ""
    assert body.splitlines()[:1] == ["FIN1"]


def test_fs02_live_nam() -> None:
    """sting records the passed thread name."""
    _assert_native()
    _sting(TH, VERB, DEST)
    body = DEST.read_text() if DEST.exists() else ""
    assert f"thread={TH}" in body.splitlines()


def test_fs03_held_verb() -> None:
    """sting records a held-out op string."""
    _assert_native()
    _sting(TH, VERB, DEST)
    body = DEST.read_text() if DEST.exists() else ""
    assert f"op={VERB}" in body.splitlines()


def test_fs04_close_mark() -> None:
    """sting dest ends with the END line."""
    _assert_native()
    _sting(TH, VERB, DEST)
    body = DEST.read_text() if DEST.exists() else ""
    assert body.endswith("END\n")


def test_fs05_long_verb() -> None:
    """sting records a holdout op string unseen in desk notes."""
    _assert_native()
    alt = Path("/app/bloturn/second.rec")
    _sting(TH, VERB2, alt)
    body = alt.read_text() if alt.exists() else ""
    assert f"op={VERB2}" in body.splitlines()


def test_fs06_pair_same() -> None:
    """sting and ease name the same thread for matching arguments."""
    _assert_native()
    a = Path("/app/bloturn/pair-a.rec")
    b = Path("/app/bloturn/pair-b.rec")
    _sting(TH, VERB, a)
    ease = _ease(TH, VERB, b)
    assert ease.returncode == 0, ease.stderr
    sa = a.read_text() if a.exists() else ""
    sb = b.read_text() if b.exists() else ""
    assert f"thread={TH}" in sa.splitlines()
    assert f"thread={TH}" in sb.splitlines()


def test_fs07_bin_magic() -> None:
    """mill is ELF and sting dest is a whole four-line card."""
    _assert_native()
    _sting(TH, VERB, DEST)
    assert DEST.read_text() == _card(TH, VERB)


def test_fs08_one_proc() -> None:
    """one sting subprocess leaves the whole dest card."""
    _assert_native()
    proc = _sting(TH, VERB, DEST)
    assert proc.returncode != 0
    assert DEST.read_text() == _card(TH, VERB)


def test_fs09_read_code() -> None:
    """look exits 0; stdout independently matches the dest file after sting."""
    _assert_native()
    _sting(TH, VERB, DEST)
    got = _look(DEST)
    assert got.returncode == 0, got.stderr
    assert got.stdout == _card(TH, VERB)


def test_fs10_bad_root() -> None:
    """ease outside bloturn exits nonzero and does not leave a success card."""
    _assert_native()
    outside = Path("/tmp/finspool-out.rec")
    if outside.exists():
        outside.unlink()
    proc = _ease(TH, VERB, outside)
    assert proc.returncode != 0
    if outside.exists():
        text = outside.read_text()
        assert text != _card(TH, VERB)


def test_fs11_dirty_redo() -> None:
    """sting recovers a whole dest after a smashed card."""
    _assert_native()
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text("nope\n")
    _sting(TH, VERB, DEST)
    assert DEST.read_text() == _card(TH, VERB)


def test_fs12_zero_body() -> None:
    """sting dest is exactly the four required lines."""
    _assert_native()
    _sting("n1", "v1", DEST)
    assert DEST.read_text() == _card("n1", "v1")


def test_fs13_hyphen_hold() -> None:
    """holdout hyphen thread survives sting as one token, not a bag split."""
    _assert_native()
    _sting(HOLD_TH, HOLD_OP, DEST)
    body = DEST.read_text() if DEST.exists() else ""
    assert body == _card(HOLD_TH, HOLD_OP)


def test_fs14_look_hold() -> None:
    """look reprints the hyphen holdout card independently of the dest path."""
    _assert_native()
    _sting(HOLD_TH, HOLD_OP, DEST)
    got = _look(DEST)
    assert got.returncode == 0, got.stderr
    assert got.stdout == _card(HOLD_TH, HOLD_OP)


def test_fs15_bait_root() -> None:
    """ease on a bloturn-named path outside the dest tree exits nonzero."""
    _assert_native()
    bait = Path("/tmp/bloturn-bait.rec")
    if bait.exists():
        bait.unlink()
    proc = _ease(TH, VERB, bait)
    assert proc.returncode != 0
    if bait.exists():
        text = bait.read_text()
        assert text != _card(TH, VERB)


def test_fs16_rip_whole_or_absent() -> None:
    """interrupted sting leaves dest whole or missing, never a partial card."""
    _assert_native()
    rip = Path("/app/opsleaf/RIP")
    DEST.parent.mkdir(parents=True, exist_ok=True)
    if DEST.exists():
        DEST.unlink()
    rip.write_text("1\n")
    try:
        _sting(TH, VERB, DEST)
        if DEST.exists():
            assert DEST.read_text() == _card(TH, VERB)
    finally:
        if rip.exists():
            rip.unlink()


def test_fs17_rip_then_restore() -> None:
    """interrupted sting then a later sting recovers a whole dest."""
    _assert_native()
    rip = Path("/app/opsleaf/RIP")
    DEST.parent.mkdir(parents=True, exist_ok=True)
    if DEST.exists():
        DEST.unlink()
    rip.write_text("1\n")
    try:
        _sting(TH, VERB, DEST)
    finally:
        if rip.exists():
            rip.unlink()
    _sting(TH, VERB, DEST)
    assert DEST.read_text() == _card(TH, VERB)
