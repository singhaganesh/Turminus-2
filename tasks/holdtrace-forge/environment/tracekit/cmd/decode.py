"""Holdtrace decode subcommand."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tracekit.runtime import reader as rmod


def run(args: argparse.Namespace) -> int:
    path = Path(args.path)
    try:
        lane_id, event, grams = rmod.ingest_blob(path.read_bytes())
    except (ValueError, OSError):
        print(json.dumps({"error": "bad_trace"}))
        return 1
    if not event:
        print(json.dumps({"error": "bad_trace"}))
        return 1
    print(json.dumps({"event": event, "lane_id": lane_id, "grams": grams}))
    return 0
