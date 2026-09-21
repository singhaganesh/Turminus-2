"""Verifier for loomketch bind artifacts."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

BIN = Path("/app/bin/loomketch")
VAT = Path("/app/vatlogs")
INK = Path("/app/inkbay")
BOUND = INK / "bound.json"
DESK = INK / "desk.tsv"
GUARD = INK / "GUARD"


def _assert_native() -> None:
    assert BIN.read_bytes()[:4] == b"\x7fELF"


def _restore() -> None:
    VAT.mkdir(parents=True, exist_ok=True)
    for p in VAT.glob("*"):
        if p.is_file():
            p.unlink()
    seed = Path("/app/seed/vatlogs")
    for p in seed.glob("*"):
        shutil.copy(p, VAT / p.name)


def _bind(root: str | None = None) -> subprocess.CompletedProcess[str]:
    _assert_native()
    if root is None:
        return subprocess.run(
            ["/app/bin/loomketch", "bind"],
            capture_output=True,
            text=True,
        )
    return subprocess.run(
        ["/app/bin/loomketch", "bind", root],
        capture_output=True,
        text=True,
    )


def _load() -> dict:
    return json.loads(BOUND.read_text())


def _desk_rows() -> list[tuple[str, str, str]]:
    lines = DESK.read_text().splitlines()
    assert lines[0] == "issue\tkind\tbody"
    rows = []
    for line in lines[1:]:
        if not line.strip():
            continue
        issue, kind, body = line.split("\t", 2)
        rows.append((issue, kind, body))
    return rows


def _bodies(data: dict) -> set[str]:
    return {f["body"] for f in data["findings"]}


def test_lk02_dir_layout_twice():
    """Relaying the same journals in a new directory layout keeps bytes."""
    _restore()
    assert _bind().returncode == 0
    first_b = BOUND.read_bytes()
    first_d = DESK.read_bytes()
    names = sorted(p.name for p in VAT.glob("*.asan"))
    blobs = {p.name: p.read_bytes() for p in VAT.glob("*.asan")}
    for p in VAT.glob("*.asan"):
        p.unlink()
    for name in reversed(names):
        (VAT / name).write_bytes(blobs[name])
    assert _bind().returncode == 0
    assert BOUND.read_bytes() == first_b
    assert DESK.read_bytes() == first_d
    for name in names:
        (VAT / name).write_bytes(blobs[name])


def test_lk03_rename_worker_files():
    """Renaming worker journals without changing texts keeps issue-to-body map."""
    _restore()
    assert _bind().returncode == 0
    before = {f["issue"]: f["body"] for f in _load()["findings"]}
    mapping = []
    for i, p in enumerate(sorted(VAT.glob("*.asan"))):
        dest = VAT / f"w_{i}.log"
        p.rename(dest)
        mapping.append(dest)
    assert _bind().returncode == 0
    after = {f["issue"]: f["body"] for f in _load()["findings"]}
    assert after == before
    _restore()


def test_lk04_set_equals_corpus():
    """Duplicate worker reports of one bug collapse to one finding body."""
    _restore()
    assert _bind().returncode == 0
    data = _load()
    bodies = [f["body"] for f in data["findings"]]
    assert len(bodies) == len(set(bodies))
    joined = " ".join(bodies)
    assert "widget_free" in joined
    assert "__asan" not in joined
    assert "__interceptor" not in joined


def test_lk05_row_keeps_same_text():
    """Each desk issue cites the same body as the bound record."""
    _restore()
    assert _bind().returncode == 0
    data = _load()
    by_issue = {int(f["issue"]): f["body"] for f in data["findings"]}
    for issue, _kind, body in _desk_rows():
        assert by_issue[int(issue)] == body


def test_lk06_ids_from_one():
    """Issue numbers start at 1 and cover each finding once."""
    _restore()
    assert _bind().returncode == 0
    issues = sorted(int(f["issue"]) for f in _load()["findings"])
    assert issues[0] == 1
    assert issues == list(range(1, len(issues) + 1))
    ordered = [f["body"] for f in sorted(_load()["findings"], key=lambda x: int(x["issue"]))]
    assert ordered == sorted(ordered)


def test_lk07_empty_exit():
    """Empty journal makes bind exit non-zero and omits GUARD."""
    _restore()
    empty = VAT / "empty.asan"
    empty.write_text("")
    if GUARD.exists():
        GUARD.unlink()
    r = _bind()
    empty.unlink()
    assert r.returncode != 0
    assert not GUARD.exists()


def test_lk08_trunc_exit():
    """Truncated journal without frames exits non-zero and omits GUARD."""
    _restore()
    trunc = VAT / "trunc.asan"
    trunc.write_text("==9==ERROR: AddressSanitizer: heap-use-after-free on address 0x1\n")
    if GUARD.exists():
        GUARD.unlink()
    r = _bind()
    trunc.unlink()
    assert r.returncode != 0
    assert not GUARD.exists()


def test_lk09_outside_refused():
    """A root outside /app/vatlogs fails and does not write GUARD."""
    _restore()
    other = Path("/tmp/loom_out")
    if other.exists():
        shutil.rmtree(other)
    other.mkdir()
    sample = next(VAT.glob("*.asan"))
    shutil.copy(sample, other / "x.asan")
    if GUARD.exists():
        GUARD.unlink()
    r = _bind(str(other))
    shutil.rmtree(other)
    assert r.returncode != 0
    assert not GUARD.exists()


def test_lk10_marker_text():
    """Successful bind writes GUARD containing ok."""
    _restore()
    if GUARD.exists():
        GUARD.unlink()
    assert _bind().returncode == 0
    assert GUARD.read_text() == "ok"
    rows = _desk_rows()
    data = _load()
    assert len(rows) == len(data["findings"])
    by_issue = {int(f["issue"]): f["body"] for f in data["findings"]}
    for issue, _kind, body in rows:
        assert by_issue[int(issue)] == body


def test_lk12_unseen_corpus():
    """Held-out journals with new hex still collapse by clipped frames."""
    _restore()
    held = VAT / "held_z.asan"
    held.write_text(
        "==77==ERROR: AddressSanitizer: heap-use-after-free on address 0xfeed\n"
        "    #0 0x1111 in __asan::ReportGenericError asan.cpp:1\n"
        "    #1 0x2222 in __interceptor_free interceptors.cpp:8\n"
        "    #2 0x3333 in widget_free src/widget_free.c:9\n"
        "    #3 0x4444 in worker_main src/worker_main.c:40\n"
    )
    r = _bind()
    held.unlink()
    assert r.returncode == 0
    bodies = _bodies(_load())
    assert any("widget_free" in b and "worker_main" in b for b in bodies)
    # still one uaf body, not a second copy keyed by hex
    uaf = [b for b in bodies if "widget_free" in b]
    assert len(uaf) == 1
