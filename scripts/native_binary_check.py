#!/usr/bin/env python3
"""GAMEABLE-NATIVE gate (deterministic).

Catches the anti-cheat hole where the instruction requires a native binary
(a compiled ELF at some /app path, "not a script/interpreter") but the graded
suite never asserts the binary is actually native. An agent then replaces the
binary with a script/interpreter mill that emits correct output and passes every
test -- the classic R7=1 GAMEABLE defect that bounces back from review.

The check is one-sided by design: it fires ONLY when the instruction genuinely
requires native. It never demands an ELF assert on a task that does not require
one (that would be scenery / UNSPECIFIED-GRADING).

    python3 native_binary_check.py <task-dir> [--json] [--strict]

Exit: 1 on BLOCKER under --strict (native required, no ELF assert), else 0.
2 when the task dir is missing.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Instruction signals that a native/compiled binary is REQUIRED.
NATIVE_REQ = re.compile(
    r"\bELF\b|7f\s*ELF|\\x7fELF|\bnative (?:elf|go|binary|executable|mill|program)\b|"
    r"compiled (?:binary|executable|program)|not (?:a|an) (?:script|interpreter|shell)|"
    r"(?:script|interpreter|shell script) (?:at that path )?(?:is )?not enough|"
    r"must be (?:a )?(?:native|compiled|an elf)",
    re.I)

# Test-side signals that the suite ASSERTS the binary is native/ELF.
ELF_ASSERT = re.compile(
    r"\\x7fELF|b?['\"]\\x7f['\"]|\bELF\b|"
    r"\.read\(\s*4\s*\)|read\(\s*4\s*\)|"
    r"magic|\bfile\b[^\n]*(?:ELF|-b )|"
    r"is_elf|check_elf|assert_elf|elf_magic",
    re.I)

# Words that make an "ELF"/"binary" mention in the instruction clearly a
# requirement rather than incidental (kept broad; NATIVE_REQ already gates).


def read(p: Path) -> str:
    try:
        return p.read_text(errors="ignore")
    except OSError:
        return ""


def instruction_text(task_dir: Path) -> str:
    parts = []
    top = task_dir / "instruction.md"
    if top.is_file():
        parts.append(read(top))
    steps = task_dir / "steps"
    if steps.is_dir():
        for p in sorted(steps.rglob("instruction.md")):
            parts.append(read(p))
    return "\n".join(parts)


def test_text(task_dir: Path) -> str:
    parts = []
    for base in (task_dir / "tests", task_dir / "steps"):
        if base.is_dir():
            for p in sorted(base.rglob("*.py")):
                parts.append(read(p))
            for p in sorted(base.rglob("test*.sh")):
                parts.append(read(p))
    return "\n".join(parts)


def evaluate(task_dir: Path) -> dict[str, object]:
    instr = instruction_text(task_dir)
    tests = test_text(task_dir)
    req_m = NATIVE_REQ.search(instr)
    requires_native = bool(req_m)
    asserts_elf = bool(ELF_ASSERT.search(tests))

    if not requires_native:
        status = "N/A"
        detail = ("instruction does not require a native binary; no ELF assert "
                  "needed (adding one would be scenery)")
    elif asserts_elf:
        status = "PASS"
        detail = "instruction requires native and the suite asserts ELF/native magic"
    else:
        status = "FAIL"
        detail = ("instruction requires a native binary but no test asserts it is "
                  "ELF/native; a script/interpreter mill that emits correct output "
                  "will pass (GAMEABLE, R7=1)")

    return {
        "task_dir": task_dir.as_posix(),
        "status": status,
        "requires_native": requires_native,
        "native_signal": (req_m.group(0) if req_m else ""),
        "asserts_elf": asserts_elf,
        "detail": detail,
        "repair": ("" if status != "FAIL" else
                   "Add a test that reads the first 4 bytes of the required "
                   "binary AFTER the rebuild/brew step and asserts they equal "
                   "b'\\x7fELF'. Run it post-build so it flips (fails on NOP, "
                   "passes after oracle), not on a prebuilt binary."),
    }


def render_human(report: dict[str, object]) -> str:
    lines = [f"STATUS: {report['status']}"]
    if report["requires_native"]:
        lines.append(f"native required (signal: {report['native_signal']!r}); "
                     f"suite asserts ELF: {report['asserts_elf']}")
    lines.append(f"  {report['detail']}")
    if report["status"] == "FAIL":
        lines.append(f"  repair: {report['repair']}")
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="GAMEABLE-NATIVE gate: native binary required but no ELF assert.")
    parser.add_argument("task_dir", type=Path, help="Path to tasks/<task>")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON only")
    parser.add_argument("--strict", action="store_true",
                        help="Accepted for runner symmetry; FAIL always exits 1 and "
                             "the runner decides block (strict) vs warn (rollout)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.task_dir.is_dir():
        print(f"native_binary_check.py: task dir not found: {args.task_dir}",
              file=sys.stderr)
        return 2
    report = evaluate(args.task_dir)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_human(report))
    return 1 if report["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
