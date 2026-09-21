"""Compile driver."""

from __future__ import annotations

import sys

from codemill.tablegen.publish import emit_map


def run_tablegen() -> int:
    emit_map()
    print("tablegen done", file=sys.stderr)
    return 0
