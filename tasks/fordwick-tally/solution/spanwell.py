#!/usr/bin/env python3
from __future__ import annotations

import sys

from spout import dump_sheet, emit_span


def main() -> int:
    if len(sys.argv) != 2:
        return 2
    n = emit_span(sys.argv[1])
    if n is None:
        return 1
    dump_sheet(n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
