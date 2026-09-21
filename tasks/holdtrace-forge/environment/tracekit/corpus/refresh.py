"""Refresh corpus traces from the live writer."""

from __future__ import annotations

from pathlib import Path

from pkgb.step_b import step_b
from tracekit.runtime import writer as wmod

CORPUS = Path("/app/tracekit/corpus")


def refresh_pool() -> None:
    schema = step_b()
    CORPUS.mkdir(parents=True, exist_ok=True)
    for old in CORPUS.glob("*.trc"):
        old.unlink()
    for idx, row in enumerate(schema.get("corpus_events", [])):
        blob = wmod.emit_lane(int(row["lane_id"]), str(row["event"]), int(row["grams"]))
        (CORPUS / f"sample_{idx}.trc").write_bytes(blob)
