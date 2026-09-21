"""Crashrail command-line front door."""

from __future__ import annotations

import argparse
import json

from codemill.tablegen.driver import run_tablegen
from relaydesk.switchboard.direct import direct


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="crashrail")
    sub = parser.add_subparsers(dest="cmd", required=True)

    route = sub.add_parser("route")
    route.add_argument("--signature", required=True)

    sub.add_parser("compile")

    args = parser.parse_args(argv)
    if args.cmd == "compile":
        return run_tablegen()
    if args.cmd == "route":
        team, source = direct(args.signature)
        print(json.dumps({"team": team, "source": source}))
        return 1 if source == "default" else 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
