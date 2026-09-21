"""Holdtrace command-line entry."""

from __future__ import annotations

import argparse

from tracekit.cmd import decode, forge, record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="holdtrace")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("forge")
    rec = sub.add_parser("record")
    rec.add_argument("--lane", type=int, required=True)
    rec.add_argument("--event", required=True)
    rec.add_argument("--grams", type=int, required=True)
    rec.add_argument("--out", default="")
    dec = sub.add_parser("decode")
    dec.add_argument("path")
    args = parser.parse_args(argv)
    if args.cmd == "forge":
        return forge.run(args)
    if args.cmd == "record":
        return record.run(args)
    if args.cmd == "decode":
        return decode.run(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
