#!/usr/bin/env python3
"""Probe that only checks the routing map file exists."""

from __future__ import annotations

from pathlib import Path

TARGET = Path("/app/relaydesk/gen/routing_map.py")


def main() -> int:
    if TARGET.is_file() and TARGET.stat().st_size > 0:
        print("map_present")
        return 0
    print("map_missing")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
