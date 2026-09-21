"""Verifier for holdtrace forge and decode behavior."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ARCHIVE = Path("/app/archive/deployed/lane_ops.trc")
CORPUS = Path("/app/tracekit/corpus")
RUNTIME = Path("/app/tracekit/runtime")
READER = RUNTIME / "reader.py"
WRITER = RUNTIME / "writer.py"
RECORD_OUT = Path("/tmp/holdtrace_grade.trc")
BIND_VARS = Path("/app/pkga/vars.py")
STENCIL_SYNC = Path("/app/pkgb/sync.py")
SCHEMA = Path("/app/tracekit/schema/span.json")


def _decode(path: Path) -> tuple[dict, int]:
    r = subprocess.run(
        ["/app/bin/holdtrace", "decode", str(path)], capture_output=True, text=True
    )
    line = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    try:
        return json.loads(line), r.returncode
    except json.JSONDecodeError:
        return {}, r.returncode


def _record(lane: int, event: str, grams: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "/app/bin/holdtrace",
            "record",
            "--lane",
            str(lane),
            "--event",
            event,
            "--grams",
            str(grams),
            "--out",
            str(RECORD_OUT),
        ],
        capture_output=True,
        text=True,
    )


def _writer_magic() -> bytes:
    text = WRITER.read_text()
    for line in text.splitlines():
        if line.strip().startswith("MAGIC"):
            frag = line.partition("=")[2].strip()
            return bytes(eval(frag))
    raise AssertionError("writer magic missing")


def _reader_magics() -> set[bytes]:
    text = READER.read_text()
    magics: set[bytes] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not (
            stripped.startswith("MAGIC")
            or stripped.startswith("ACCEPT")
            or stripped.startswith("MAGICS")
        ):
            continue
        frag = line.partition("=")[2].strip()
        if frag.startswith("("):
            for part in frag.strip("()").split(","):
                part = part.strip()
                if part.startswith("b"):
                    magics.add(bytes(eval(part)))
        elif frag.startswith("b"):
            magics.add(bytes(eval(frag)))
    return magics


def test_span_ctx_exports_legacy_magic():
    """span_ctx must export legacy_magic from span.json for template rendering."""
    import sys

    sys.path.insert(0, "/app")
    from pkga.vars import span_ctx

    schema = json.loads(Path("/app/tracekit/schema/span.json").read_text())
    ctx = span_ctx(schema)
    assert ctx.get("legacy_magic") == "HLT1"
    assert ctx.get("magic") == "HLT2"
    assert ctx.get("name_len_bits") == 16


def test_forge_renders_consume_template():
    """emit_runtime must render rdr.tpl through render_tpl, not copy it verbatim."""
    body = STENCIL_SYNC.read_text()
    assert 'render_tpl("rdr.tpl"' in body or "render_tpl('rdr.tpl'" in body
    assert '(pkgc / "rdr.tpl").read_text()' not in body


def test_pipeline_magic_alignment():
    """Reader must accept the writer magic constant on generated runtime modules."""
    assert _writer_magic() in _reader_magics()


def test_vault_payload_fields():
    """Archived deployment trace must decode to lane_open with lane 7 and 1250 grams."""
    blob = ARCHIVE.read_bytes()
    assert blob[:4] == b"HLT1"
    assert _writer_magic() == b"HLT2"
    data, code = _decode(ARCHIVE)
    assert code == 0
    assert data == {"event": "lane_open", "lane_id": 7, "grams": 1250}


def test_live_emit_roundtrip():
    """A newly recorded trace must decode to the same event, lane, and grams."""
    assert _record(5, "sort_gate", 2200).returncode == 0
    data, code = _decode(RECORD_OUT)
    assert code == 0
    assert data == {"event": "sort_gate", "lane_id": 5, "grams": 2200}


def test_pool_samples_decode():
    """Every corpus trace must decode through the CLI and use the writer magic prefix."""
    wm = _writer_magic()
    samples = sorted(CORPUS.glob("*.trc"))
    assert samples, "corpus missing; run holdtrace forge after repairing sources"
    for path in samples:
        assert path.read_bytes()[:4] == wm
        data, code = _decode(path)
        assert code == 0
        assert "event" in data and "lane_id" in data and "grams" in data


def test_size_probe_insufficient():
    """Corpus size smoke passing must not excuse a broken archive decode."""
    smoke = subprocess.run(
        ["/app/tracekit/smoke/corpus_len.py"], capture_output=True, text=True
    )
    assert smoke.returncode == 0
    data, code = _decode(ARCHIVE)
    assert code == 0
    assert data.get("grams") == 1250


def test_junk_rejected_valid_persists():
    """Random bytes must fail decode while the archive still decodes afterward."""
    junk = Path("/tmp/holdtrace_junk.trc")
    junk.write_bytes(b"NOPE" + b"\x00" * 12)
    data, code = _decode(junk)
    assert code != 0
    assert data.get("error") == "bad_trace"
    good, gcode = _decode(ARCHIVE)
    assert gcode == 0
    assert good.get("event") == "lane_open"


def test_first_sample_fields():
    """First corpus sample must decode to dock_idle on lane 3 with 400 grams."""
    data, code = _decode(CORPUS / "sample_0.trc")
    assert code == 0
    assert data == {"event": "dock_idle", "lane_id": 3, "grams": 400}


def test_second_sample_fields():
    """Second corpus sample must decode to lift_done on lane 11 with 980 grams."""
    data, code = _decode(CORPUS / "sample_1.trc")
    assert code == 0
    assert data == {"event": "lift_done", "lane_id": 11, "grams": 980}


def test_name_width_sixteen():
    """Reader must use sixteen-bit name lengths after forge matches the schema."""
    text = READER.read_text()
    assert "NAME_BITS = 16" in text
    data, code = _decode(ARCHIVE)
    assert code == 0


def test_emit_nonempty_blob():
    """Record must emit a trace that decodes with the expected lane and grams."""
    assert _record(2, "weigh_in", 55).returncode == 0
    assert RECORD_OUT.exists()
    assert len(RECORD_OUT.read_bytes()) >= 12
    data, code = _decode(RECORD_OUT)
    assert code == 0
    assert data == {"event": "weigh_in", "lane_id": 2, "grams": 55}


def test_revision_tag_two():
    """Span schema version must remain two and archive decode must stay valid."""
    schema = json.loads(Path("/app/tracekit/schema/span.json").read_text())
    assert schema.get("version") == 2
    text = READER.read_text()
    assert "schema v2" in text
    data, code = _decode(ARCHIVE)
    assert code == 0
    assert data == {"event": "lane_open", "lane_id": 7, "grams": 1250}
