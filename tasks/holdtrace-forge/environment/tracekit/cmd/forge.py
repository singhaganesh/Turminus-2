"""Holdtrace forge subcommand."""

from __future__ import annotations

import argparse

from pkgb.sync import emit_runtime


def run(_: argparse.Namespace) -> int:
    emit_runtime()
    return 0
