"""Regenerate runtime modules and corpus from span.json."""

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
    pkgc = Path(__file__).resolve().parent.parent / "pkgc"
    (runtime / "reader.py").write_text((pkgc / "rdr.tpl").read_text())
    refresh_pool()


if __name__ == "__main__":
    emit_runtime()
    print("forge complete", file=sys.stderr)
