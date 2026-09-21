#!/bin/bash
set -euo pipefail

python3 << 'PY'
from pathlib import Path

pkga = Path("/app/pkga/vars.py")
pkga.write_text(
    '''"""Map span schema fields into template substitution context."""

from __future__ import annotations

from typing import Any


def _coerce_magic(raw: Any) -> str:
    if isinstance(raw, str) and len(raw) == 4:
        return raw
    return "HLT2"


def _coerce_legacy(raw: Any, current: str) -> str:
    if isinstance(raw, str) and len(raw) == 4:
        return raw
    return "HLT1"


def span_ctx(schema: dict) -> dict:
    magic = _coerce_magic(schema.get("magic", "HLT2"))
    legacy = _coerce_legacy(schema.get("legacy_magic", "HLT1"), magic)
    bits = int(schema.get("name_len_bits", 16))
    if bits not in (8, 16):
        bits = 16
    return {
        "version": int(schema.get("version", 1)),
        "magic": magic,
        "legacy_magic": legacy,
        "name_len_bits": bits,
    }
'''
)

pkgb = Path("/app/pkgb/sync.py")
pkgb.write_text(
    '''"""Regenerate runtime modules and corpus from span.json."""

from __future__ import annotations

import sys
from pathlib import Path

from pkga.vars import span_ctx
from pkgb.render import render_tpl
from pkgb.step_b import step_b
from tracekit.corpus.refresh import refresh_pool


def emit_runtime() -> None:
    schema = step_b()
    ctx = span_ctx(schema)
    runtime = Path("/app/tracekit/runtime")
    runtime.mkdir(parents=True, exist_ok=True)
    (runtime / "writer.py").write_text(render_tpl("wrt.tpl", ctx))
    (runtime / "reader.py").write_text(render_tpl("rdr.tpl", ctx))
    refresh_pool()


if __name__ == "__main__":
    emit_runtime()
    print("forge complete", file=sys.stderr)
'''
)

pkgc = Path("/app/pkgc/rdr.tpl")
pkgc.write_text(
    '''"""Generated trace reader (schema v{{ version }})."""

from __future__ import annotations

from tracekit.runtime.pack import decode_trace

MAGICS = (b"{{ legacy_magic }}", b"{{ magic }}")
NAME_BITS = {{ name_len_bits }}


def _validate_event(name: str) -> str:
    if not name:
        raise ValueError("empty event")
    if chr(0) in name:
        raise ValueError("embedded nul")
    return name


def ingest_blob(blob: bytes) -> tuple[int, str, int]:
    if not blob:
        raise ValueError("empty")
    lane_id, event, grams = decode_trace(blob, MAGICS, NAME_BITS)
    event = _validate_event(event)
    if grams < 0:
        raise ValueError("negative grams")
    return lane_id, event, grams
'''
)
print("patched pkga, pkgb, pkgc")
PY

/app/bin/holdtrace forge

python3 << 'PY'
import json
import subprocess

archive = subprocess.run(
    ["/app/bin/holdtrace", "decode", "/app/archive/deployed/lane_ops.trc"],
    capture_output=True,
    text=True,
    check=True,
)
data = json.loads(archive.stdout.strip().splitlines()[-1])
if data != {"event": "lane_open", "lane_id": 7, "grams": 1250}:
    raise SystemExit("archive mismatch")
print("oracle ok")
PY
