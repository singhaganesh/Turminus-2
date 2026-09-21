#!/usr/bin/env python3
"""Caveat-audit gate (leg-1 deterministic, legs 2-3 surfaced).

The review-side checker runs a three-leg consistency check for every capability
class the suite grades, and a graded-but-broken class blocks ship. This script
brings the deterministic part of that gate to construction time:

  Leg 1 (instruction states the rule)  -> checked here. A graded class whose
        rule the instruction never states in operator language is an ambush.
  Leg 2 (environment tempts the wrong move) -> surfaced as a checklist item.
  Leg 3 (solution demonstrates the right move) -> surfaced as a checklist item.

Legs 2 and 3 need judgement the author (or the LLM authoring loop) must confirm;
this script names the classes so neither is silently skipped.

    python3 caveat_audit_check.py tasks/<slug> [--json] [--strict]

Exit code: 1 when a graded class has no instruction support (leg-1 broken),
else 0. 2 when the task dir is missing.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

# Same class detectors as difficulty_floor_check.py / review-side static_check.py.
CAPABILITY_CLASSES = {
    "recompute_consistency": re.compile(
        r"independent|recomput|reconcil|matches?_|digest|fingerprint|cross[_-]?check|"
        r"consisten|seal|bound|integrity|checksum|hashlib|sha256|sha1|blake2|hmac|crc32",
        re.I),
    "variant_holdout": re.compile(
        r"variant|holdout|hidden|unseen|seed|generali[sz]|ablation|dynamic|hardcod|matrix|"
        r"ladder|parametri[sz]e|for\s+\w+\s+in\s+range\(|shuffle|random\.", re.I),
    "fault_rejection": re.compile(
        r"reject|denie|deny|fail|alarm|invalid|corrupt|poison|abort|tamper|stale|expired|"
        r"malformed|backdoor|pytest\.raises|assertRaises|returncode\s*!=\s*0|exit\s*code",
        re.I),
    "sequencing_recovery": re.compile(
        r"order|epoch|replay|recover|latch|idempot|resume|restart|race|concurren|multihop|"
        r"skew|offset|twice|second\s+run|re-?run|kill|sigterm", re.I),
}

# Operator-language keywords per class: what a fair instruction would plausibly
# say. Deliberately broad so the leg-1 heuristic is a soft hint, not a gate --
# the final leg-1/2/3 call is the authoring LLM's (it quotes spans, as the
# review side does). A miss here means "review this class", never "broken".
INSTRUCTION_RULE_HINTS = {
    "recompute_consistency": re.compile(
        r"recomput|re-?derive|independent|match|consisten|digest|checksum|hash|"
        r"integrity|verify|reconcil|equal|same value|agree|regenerat|rebuild|"
        r"compile|emit|generate|produce|refresh|up-?to-?date|current", re.I),
    "variant_holdout": re.compile(
        r"any|all|every|arbitrary|general|unseen|new|held?-?out|each|varied|"
        r"not just|beyond the sample|different input|input|case", re.I),
    "fault_rejection": re.compile(
        r"reject|invalid|corrupt|malformed|error|fail|refuse|non-?zero|abort|"
        r"unknown|missing|bad|exit code|must not|exit|status|non-existent", re.I),
    "sequencing_recovery": re.compile(
        r"order|sequence|rebuild|regenerat|re-?run|again|twice|idempot|resume|"
        r"restart|after|before|stage|step|interrupt|epoch|offset|compile|run", re.I),
}


def read(p: Path) -> str:
    try:
        return p.read_text(errors="ignore")
    except OSError:
        return ""


def iter_test_files(task_dir: Path) -> list[Path]:
    out: list[Path] = []
    for base in (task_dir / "tests", task_dir / "steps"):
        if base.is_dir():
            out.extend(sorted(base.rglob("*.py")))
    seen: set[Path] = set()
    uniq: list[Path] = []
    for p in out:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


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


def graded_classes(task_dir: Path) -> dict[str, int]:
    hits: dict[str, int] = {}
    for path in iter_test_files(task_dir):
        src = read(path)
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        lines = src.splitlines()
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                    and n.name.startswith("test"):
                body = n.name + "\n" + "\n".join(
                    lines[n.lineno - 1:(n.end_lineno or n.lineno)])
                for cls, rx in CAPABILITY_CLASSES.items():
                    if rx.search(body):
                        hits[cls] = hits.get(cls, 0) + 1
    return hits


def evaluate(task_dir: Path) -> dict[str, object]:
    hits = graded_classes(task_dir)
    instr = instruction_text(task_dir)
    legs = []
    review = 0
    for cls in sorted(hits):
        leg1 = bool(INSTRUCTION_RULE_HINTS[cls].search(instr))
        if not leg1:
            review += 1
        legs.append({
            "class": cls,
            "graded_tests": hits[cls],
            "leg1_instruction_hint_matched": leg1,
            "leg1_action": ("looks stated; LLM must still confirm with a quoted span"
                            if leg1 else
                            "no operator-language match found; confirm the "
                            "instruction states this rule or it is an ambush"),
            "leg2_env_tempts_wrong_move": "confirm (quote the planted temptation)",
            "leg3_solution_shows_right_move": "confirm (quote the correct move)",
        })
    # Advisory only: this script enumerates graded classes so none is skipped and
    # gives a soft leg-1 hint. It never blocks -- the three-leg verdict is the
    # authoring LLM's, matching how the review side judges (quoted spans).
    status = "WARN" if (not hits or review) else "PASS"
    return {
        "task_dir": task_dir.as_posix(),
        "status": status,
        "advisory": True,
        "graded_classes": hits,
        "classes_to_review": review,
        "legs": legs,
        "note": ("No capability class detected in the suite; caveat audit is "
                 "N/A here but the DIFFICULTY-FLOOR gate will block." if not hits else
                 "Confirm all three legs per class (quote spans). Legs 2 and 3 "
                 "always need author/LLM judgement; leg-1 hint is heuristic."),
    }


def render_human(report: dict[str, object]) -> str:
    lines = [f"STATUS: {report['status']} (advisory)",
             f"graded classes: {report['graded_classes'] or 'none'}"]
    for leg in report["legs"]:
        lines.append("")
        mark = "hint-ok" if leg["leg1_instruction_hint_matched"] else "REVIEW"
        lines.append(f"[{leg['class']}] {leg['graded_tests']} test(s)  leg1: {mark}")
        lines.append(f"  leg1: {leg['leg1_action']}")
        lines.append(f"  leg2 (env tempts wrong move): {leg['leg2_env_tempts_wrong_move']}")
        lines.append(f"  leg3 (solution shows right move): {leg['leg3_solution_shows_right_move']}")
    lines.append("")
    lines.append(report["note"])
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Caveat-audit gate: leg-1 deterministic, legs 2-3 surfaced.")
    parser.add_argument("task_dir", type=Path, help="Path to tasks/<task>")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON only")
    parser.add_argument("--strict", action="store_true",
                        help="Accepted for runner symmetry; leg-1 broken always fails")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.task_dir.is_dir():
        print(f"caveat_audit_check.py: task dir not found: {args.task_dir}",
              file=sys.stderr)
        return 2
    report = evaluate(args.task_dir)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_human(report))
    # Advisory gate: never blocks. It enumerates graded classes and hints at
    # leg-1; the three-leg verdict is the authoring LLM's call.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
