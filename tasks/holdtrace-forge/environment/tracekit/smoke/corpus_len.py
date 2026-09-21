#!/usr/bin/env python3
"""Local smoke helper — only checks corpus files exist (not decode)."""

from __future__ import annotations

from pathlib import Path

CORPUS = Path("/app/tracekit/corpus")


def main() -> int:
    files = list(CORPUS.glob("*.trc"))
    if not files:
        return 1
    for p in files:
        if p.stat().st_size < 8:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
