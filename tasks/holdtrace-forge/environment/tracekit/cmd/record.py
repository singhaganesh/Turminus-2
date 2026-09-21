"""Holdtrace record subcommand."""

from __future__ import annotations

import argparse
from pathlib import Path

from tracekit.runtime import writer as wmod


def run(args: argparse.Namespace) -> int:
    blob = wmod.emit_lane(args.lane, args.event, args.grams)
    out = Path(args.out) if args.out else Path("/tmp/holdtrace_last.trc")
    out.write_bytes(blob)
    return 0
