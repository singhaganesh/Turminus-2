"""wrenkv store verifier checks.

Every check drives the public CLI in its own processes and compares the
recovered store against an independently recomputed model of the operations.
No check inspects source layout; only behavior across kill, recovery, fold,
and continuation sequences is judged.
"""

import json
import subprocess
from pathlib import Path

import pytest

BIN = "/app/bin/wrenkv"
SOURCE_ROOT = "/app/environment"
WORKLOADS = Path("/app/workloads")
SEED = 20260904


def test_torn_header_does_not_poison_prefix(tmp_path):
    """A log that ends in a mid-header tear must recover the durable prefix
    and keep covered_seq on that prefix, not fail the Go package compile."""
    store = str(tmp_path / "s")
    r = _load(store, MIXED, "--crash-tail", "3")
    assert r.returncode == 67
    rec = _run("recover", store)
    assert rec.returncode == 0, rec.stderr
    d = _dump(store)
    assert d["entries"] == _entries(_model(MIXED_OPS[:3]))
    assert d["covered_seq"] == 3


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [BIN, *args], capture_output=True, text=True, timeout=120
    )


def _load(store: str, ops_path: str, *extra: str) -> subprocess.CompletedProcess:
    return _run("load", store, "--ops", ops_path, *extra)


def _dump(store: str) -> dict:
    r = _run("dump", store)
    assert r.returncode == 0, f"dump failed: {r.returncode} {r.stderr}"
    return json.loads(r.stdout)


def _parse_ops(path: Path) -> list[dict]:
    ops = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if parts[0] == "put":
            ops.append({"op": "put", "key": parts[1], "value": parts[2]})
        elif parts[0] == "del":
            ops.append({"op": "del", "key": parts[1]})
        else:
            ops.append({"op": "incr", "key": parts[1], "delta": int(parts[2])})
    return ops


def _model(ops: list[dict]) -> dict:
    """Apply operations to an independent row model, numbering revs from 1."""
    rows: dict[str, dict] = {}
    for seq, op in enumerate(ops, 1):
        if op["op"] == "put":
            rows[op["key"]] = {"v": op["value"], "rev": seq}
        elif op["op"] == "del":
            rows.pop(op["key"], None)
        else:
            cur = int(rows[op["key"]]["v"]) if op["key"] in rows else 0
            rows[op["key"]] = {"v": str(cur + op["delta"]), "rev": seq}
    return rows


def _entries(rows: dict) -> list[dict]:
    return [
        {"key": k, "value": rows[k]["v"], "rev": rows[k]["rev"]}
        for k in sorted(rows)
    ]


def _write_ops(path: Path, ops: list[dict]) -> str:
    lines = []
    for op in ops:
        if op["op"] == "put":
            lines.append(f"put {op['key']} {op['value']}")
        elif op["op"] == "del":
            lines.append(f"del {op['key']}")
        else:
            lines.append(f"incr {op['key']} {op['delta']}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(path)


def _seeded_ops(tmp_path: Path) -> tuple[str, list[dict]]:
    """Deterministic mixed workload from a fixed LCG stream; the counter key
    only ever receives incr, so every generated file is a valid ops file."""
    state = SEED
    keys = ["k1", "k2", "k3", "x.y"]
    gen = []
    for _ in range(24):
        state = (state * 1103515245 + 12345) % 2147483648
        draw = state % 100
        state = (state * 1103515245 + 12345) % 2147483648
        key = keys[state % len(keys)]
        if draw < 50:
            state = (state * 1103515245 + 12345) % 2147483648
            gen.append({"op": "put", "key": key, "value": "v%d" % (state % 100)})
        elif draw < 70:
            gen.append({"op": "del", "key": key})
        else:
            state = (state * 1103515245 + 12345) % 2147483648
            gen.append({"op": "incr", "key": "counter", "delta": 1 + state % 8})
    return _write_ops(tmp_path / "seeded.ops", gen), gen


MIXED = str(WORKLOADS / "mixed.ops")
COUNTER = str(WORKLOADS / "tally.ops")
MIXED_OPS = _parse_ops(WORKLOADS / "mixed.ops")
COUNTER_OPS = _parse_ops(WORKLOADS / "tally.ops")


def test_clean_load_dump_exact(tmp_path):
    """A load killed at a fence, then a recovery pass killed partway, still
    leaves the store serving exactly the durable prefix with per-key revs
    from an independent model once a later recovery completes."""
    store = str(tmp_path / "s")
    r = _load(store, MIXED, "--crash-after", "5")
    assert r.returncode in (0, 67), r.stderr
    r = _run("recover", store, "--crash-after", "2")
    assert r.returncode in (0, 67), r.stderr
    assert _run("recover", store).returncode == 0
    d = _dump(store)
    assert d["covered_seq"] == 5
    assert d["entries"] == _entries(_model(MIXED_OPS[:5]))


@pytest.mark.parametrize("n", [1, 3, 7, 9, 12])
def test_crash_after_prefix(tmp_path, n):
    """After a kill at fence N and a completed recovery, exactly the first
    min(N, len) operations of the load are in the store and the progress
    coordinate covers them."""
    store = str(tmp_path / f"s{n}")
    r = _load(store, MIXED, "--crash-after", str(n))
    assert r.returncode in (0, 67), r.stderr
    assert _run("recover", store).returncode == 0
    d = _dump(store)
    assert d["covered_seq"] == min(n, len(MIXED_OPS))
    assert d["entries"] == _entries(_model(MIXED_OPS[: min(n, len(MIXED_OPS))]))


@pytest.mark.parametrize("n", [0, 2, 8])
def test_torn_tail_clean_stop(tmp_path, n):
    """A load killed mid-record tears the log tail; recovery must end
    cleanly with exit 0 and serve exactly the first n whole operations."""
    store = str(tmp_path / f"s{n}")
    r = _load(store, MIXED, "--crash-tail", str(n))
    assert r.returncode == 67
    rec = _run("recover", store)
    assert rec.returncode == 0, f"recover refused a torn tail: {rec.stderr}"
    d = _dump(store)
    assert d["entries"] == _entries(_model(MIXED_OPS[:n]))


def test_idempotent_recover(tmp_path):
    """A completed recovery serves exactly the applied operations, and two
    completed recovery passes in a row leave identical dump output, so replay
    is not applied twice anywhere in the pipeline."""
    store = str(tmp_path / "s")
    assert _load(store, MIXED).returncode == 0
    assert _run("recover", store).returncode == 0
    first = _dump(store)
    assert first["entries"] == _entries(_model(MIXED_OPS))
    assert _run("recover", store).returncode == 0
    second = _dump(store)
    assert first == second
    assert first["covered_seq"] == len(MIXED_OPS)


def test_resume_after_bake(tmp_path):
    """Load, bake, then a second killed load followed by recovery keeps the
    pre-kill operations and the post-bake prefix, with exact revs and
    covered_seq."""
    store = str(tmp_path / "s")
    assert _load(store, MIXED).returncode == 0
    assert _run("recover", store).returncode == 0
    r = _load(store, COUNTER, "--crash-after", "3")
    assert r.returncode in (0, 67)
    assert _run("recover", store).returncode == 0
    d = _dump(store)
    assert d["entries"] == _entries(_model(MIXED_OPS + COUNTER_OPS[:3]))
    assert d["covered_seq"] == len(MIXED_OPS) + 3


@pytest.mark.parametrize("n", [0, 1, 2, 3, 4, 6])
def test_compaction_crash_preserves_prefix(tmp_path, n):
    """A fold killed at any fence point leaves a store from which recovery
    restores every operation that was durable before the fold started."""
    store = str(tmp_path / f"s{n}")
    assert _load(store, MIXED).returncode == 0
    r = _run("compact", store, "--crash-after", str(n))
    assert r.returncode in (0, 67), r.stderr
    assert _run("recover", store).returncode == 0
    d = _dump(store)
    assert d["entries"] == _entries(_model(MIXED_OPS))
    assert d["covered_seq"] == len(MIXED_OPS)


@pytest.mark.parametrize("n", [0, 1, 2, 3])
def test_recovery_resume(tmp_path, n):
    """A recovery pass killed at any fence point must be resumable: the next
    recovery restores every durable operation with correct revs."""
    store = str(tmp_path / f"s{n}")
    assert _load(store, MIXED).returncode == 0
    r = _run("recover", store, "--crash-after", str(n))
    assert r.returncode in (0, 67), r.stderr
    assert _run("recover", store).returncode == 0
    d = _dump(store)
    assert d["entries"] == _entries(_model(MIXED_OPS))
    assert d["covered_seq"] == len(MIXED_OPS)


def test_counter_semantics(tmp_path):
    """incr on an absent key starts at 0, chains fold deltas in order, and
    revs point at the last writing operation, with the progress coordinate
    covering every applied operation."""
    store = str(tmp_path / "s")
    assert _load(store, COUNTER).returncode == 0
    assert _run("recover", store).returncode == 0
    d = _dump(store)
    assert d["covered_seq"] == len(COUNTER_OPS)
    assert d["entries"] == _entries(_model(COUNTER_OPS))


def test_load_error_prefix(tmp_path):
    """Invalid ops lines exit 2 before touching the store; a non-integer
    incr target exits 2 mid-run with the flushed prefix kept, and a later
    recovery covers exactly that prefix."""
    store = str(tmp_path / "s")
    bad_syntax = tmp_path / "bad.ops"
    bad_syntax.write_text("put a 1\nfrobnicate a\n", encoding="utf-8")
    r = _load(store, str(bad_syntax))
    assert r.returncode == 2
    bad_incr = tmp_path / "bad2.ops"
    bad_incr.write_text("put a 1\nput b two\nincr a 5\nincr b 1\n", encoding="utf-8")
    r = _load(store, str(bad_incr))
    assert r.returncode == 2
    expected = _model(
        [
            {"op": "put", "key": "a", "value": "1"},
            {"op": "put", "key": "b", "value": "two"},
            {"op": "put", "key": "a", "value": "6"},
        ]
    )
    d = _dump(store)
    assert d["entries"] == _entries(expected)
    assert _run("recover", store).returncode == 0
    after = _dump(store)
    assert after["entries"] == _entries(expected)
    assert after["covered_seq"] == 3


def test_seeded_convergence(tmp_path):
    """A deterministic generated workload converges to the independently
    recomputed model across crash points, a fold, a torn kill, and a
    continuation load."""
    ops_path, gen = _seeded_ops(tmp_path)

    for n in (4, 10, 16, 22):
        store = str(tmp_path / f"sweep{n}")
        r = _load(store, ops_path, "--crash-after", str(n))
        assert r.returncode in (0, 67)
        assert _run("recover", store).returncode == 0
        d = _dump(store)
        assert d["entries"] == _entries(_model(gen[:n]))

    store = str(tmp_path / "chain")
    assert _load(store, ops_path).returncode == 0
    assert _run("compact", store).returncode == 0
    r = _load(store, ops_path, "--crash-tail", "5")
    assert r.returncode == 67
    assert _run("recover", store).returncode == 0
    d = _dump(store)
    assert d["entries"] == _entries(_model(gen + gen[:5]))
    r = _load(store, ops_path, "--crash-after", "4")
    assert r.returncode in (0, 67)
    assert _run("recover", store).returncode == 0
    d = _dump(store)
    assert d["entries"] == _entries(_model(gen + gen[:5] + gen[:4]))


def test_interface_compat(tmp_path):
    """The frozen CLI surface holds on a store that went through a torn
    kill: missing store directories exit 2, and dump output carries exactly
    the documented fields and types."""
    torn = str(tmp_path / "torn")
    r = _load(torn, str(WORKLOADS / "demo.ops"), "--crash-tail", "1")
    assert r.returncode == 67
    assert _run("recover", torn).returncode == 0
    missing = str(tmp_path / "missing")
    assert _run("dump", missing).returncode == 2
    assert _run("recover", missing).returncode == 2
    d = _dump(torn)
    assert set(d.keys()) == {"covered_seq", "entries"}
    assert isinstance(d["covered_seq"], int)
    assert d["covered_seq"] == 1
    for e in d["entries"]:
        assert set(e.keys()) == {"key", "value", "rev"}
        assert isinstance(e["key"], str)
        assert isinstance(e["value"], str)
        assert isinstance(e["rev"], int)


def test_rev_visibility(tmp_path):
    """Overwrites and deletes leave revs equal to the last writing
    operation's sequence number, matching the independent model."""
    store = str(tmp_path / "s")
    ops_path = _write_ops(
        tmp_path / "ov.ops",
        [
            {"op": "put", "key": "a", "value": "1"},
            {"op": "put", "key": "b", "value": "2"},
            {"op": "incr", "key": "a", "delta": 3},
            {"op": "put", "key": "a", "value": "9"},
            {"op": "del", "key": "b"},
            {"op": "put", "key": "b", "value": "7"},
        ],
    )
    assert _load(store, ops_path).returncode == 0
    assert _run("recover", store).returncode == 0
    d = _dump(store)
    assert d["covered_seq"] == 6
    assert d["entries"] == _entries(_model(_parse_ops(Path(ops_path))))


@pytest.mark.parametrize("pre", [2, 6])
def test_torn_tail_then_continue(tmp_path, pre):
    """After a torn kill the store keeps working: a later load succeeds, its
    writes are visible in a live dump, and recovery keeps both prefixes."""
    store = str(tmp_path / f"s{pre}")
    r = _load(store, MIXED, "--crash-tail", str(pre))
    assert r.returncode == 67
    r = _load(store, COUNTER)
    assert r.returncode == 0, f"load after a torn kill failed: {r.stderr}"
    d = _dump(store)
    expected = _model(MIXED_OPS[:pre] + COUNTER_OPS)
    assert d["entries"] == _entries(expected)
    assert _run("recover", store).returncode == 0
    after = _dump(store)
    assert after["entries"] == _entries(expected)
    assert after["covered_seq"] == pre + len(COUNTER_OPS)


def test_covered_advance(tmp_path):
    """A completed recovery installs the coordination record: dump's
    covered_seq equals the highest applied sequence number."""
    store = str(tmp_path / "s")
    assert _load(store, COUNTER).returncode == 0
    assert _run("recover", store).returncode == 0
    d = _dump(store)
    assert d["covered_seq"] == len(COUNTER_OPS)


@pytest.mark.parametrize("n", [0, 1, 2, 3])
def test_resume_covered_advance(tmp_path, n):
    """After a killed recovery pass, the next completed recovery leaves
    covered_seq at the highest applied sequence and full entries."""
    store = str(tmp_path / f"s{n}")
    assert _load(store, COUNTER).returncode == 0
    r = _run("recover", store, "--crash-after", str(n))
    assert r.returncode in (0, 67)
    assert _run("recover", store).returncode == 0
    d = _dump(store)
    assert d["covered_seq"] == len(COUNTER_OPS)
    assert d["entries"] == _entries(_model(COUNTER_OPS))


def test_interleaved_recovery_resume(tmp_path):
    """A killed recovery leaves a renamed base-<gen+1>.tbl while keep.json is still
    on the prior generation. A subsequent load must still advance cleanly, and the
    next completed recovery must fold both prefixes into the active generation."""
    store = str(tmp_path / "s")
    assert _load(store, MIXED).returncode == 0
    assert _run("recover", store).returncode == 0
    # Store now has gen 1 with MIXED_OPS covered
    r = _load(store, COUNTER, "--crash-after", "4")
    assert r.returncode in (0, 67)

    # Simulate a recovery pass killed after renaming base-2.tbl but before keep.json update.
    # base-2.tbl holds rows for MIXED_OPS + COUNTER_OPS[:4]
    pfx_rows = _model(MIXED_OPS + COUNTER_OPS[:4])
    base2_snap = {
        "gen": 2,
        "seq": len(MIXED_OPS) + 4,
        "rows": pfx_rows,
    }
    base2_path = Path(store) / "base-2.tbl"
    base2_path.write_text(json.dumps(base2_snap) + "\n", encoding="utf-8")

    # Interleaved load runs before the next recover
    r = _load(store, str(WORKLOADS / "demo.ops"))
    assert r.returncode == 0, f"interleaved load failed: {r.stderr}"

    demo_ops = _parse_ops(WORKLOADS / "demo.ops")
    expected_rows = _model(MIXED_OPS + COUNTER_OPS[:4] + demo_ops)
    expected_seq = len(MIXED_OPS) + 4 + len(demo_ops)

    # Live dump before recover should see durable prefix + interleaved load
    live = _dump(store)
    assert live["entries"] == _entries(expected_rows)

    # Completed recover must rebuild and reconcile to gen 2 with full state
    assert _run("recover", store).returncode == 0
    after = _dump(store)
    assert after["entries"] == _entries(expected_rows)
    assert after["covered_seq"] == expected_seq


def test_mid_header_torn_tail(tmp_path):
    """A log ending in a torn record broken at the header where plen exceeds
    MaxPayload (rr_scan.go:64) must halt the scan cleanly without error,
    preserving preceding records and allowing subsequent appends."""
    store = str(tmp_path / "s")
    assert _load(store, MIXED, "--crash-after", "4").returncode in (0, 67)

    # Append a torn record broken at header: Magic "WRKV", seq 5, plen > MaxPayload
    # MaxPayload is 1 << 20 = 1048576 (0x00100000)
    log_path = Path(store) / "append.log"
    head = bytearray()
    head.extend(b"WRKV")                                  # magic (4 bytes)
    head.extend((5).to_bytes(8, "big"))                   # seq (8 bytes)
    head.extend((1048576 + 512).to_bytes(4, "big"))      # plen > MaxPayload (4 bytes)
    head.extend((0xDEADBEEF).to_bytes(4, "big"))          # crc (4 bytes)
    head.extend(b"torn")                                  # trailing fragment
    with open(log_path, "ab") as f:
        f.write(head)

    # Recover must halt cleanly at the torn record instead of failing with ErrTornTail
    rec = _run("recover", store)
    assert rec.returncode == 0, f"recover failed on mid-header torn tail: {rec.stderr}"

    d = _dump(store)
    expected_prefix = _model(MIXED_OPS[:4])
    assert d["entries"] == _entries(expected_prefix)
    assert d["covered_seq"] == 4

    # Subsequent load must repair/truncate the torn tail and append new records cleanly
    r = _load(store, COUNTER)
    assert r.returncode == 0, f"load after mid-header tear failed: {r.stderr}"

    expected_full = _model(MIXED_OPS[:4] + COUNTER_OPS)
    assert _run("recover", store).returncode == 0
    after = _dump(store)
    assert after["entries"] == _entries(expected_full)
    assert after["covered_seq"] == 4 + len(COUNTER_OPS)


def test_staged_tmp_artifact_ignored(tmp_path):
    """An uncommitted base-*.tbl.tmp artifact left by an interrupted bake must
    never be used to advance sequence coordinates or truncate log replay."""
    store = str(tmp_path / "s")
    assert _load(store, MIXED).returncode == 0
    # Simulate an aborted compaction that wrote an uncommitted tmp file
    fake_snap = {
        "gen": 1,
        "seq": 9999,
        "rows": {"bogus": {"v": "fake", "rev": 9999}},
    }
    tmp_artifact = Path(store) / "base-1.tbl.tmp"
    tmp_artifact.write_text(json.dumps(fake_snap) + "\n", encoding="utf-8")

    assert _run("recover", store).returncode == 0
    d = _dump(store)
    # The bogus tmp artifact must not infect the store
    assert "bogus" not in [e["key"] for e in d["entries"]]
    assert d["entries"] == _entries(_model(MIXED_OPS))
    assert d["covered_seq"] == len(MIXED_OPS)
