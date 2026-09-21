#!/usr/bin/env python3
"""DIFFICULTY-FLOOR gate (deterministic).

Ported from the review-side checker's static_check.py so authors hit the same
gate at construction time instead of on a bounce-back. The suite must exercise
at least two of the four capability classes measured to separate near-miss
failures on the 51-task / 816-rollout corpus, or one class plus >=3
execution-dependent tests.

    python3 difficulty_floor_check.py tasks/<slug> [--json] [--strict]

Classes (counts = tasks whose discriminator tests demand them):
  recompute_consistency (17)  variant_holdout (9)
  fault_rejection (10)        sequencing_recovery (17)

Exit code: 1 when the floor is not met (BLOCKER), else 0. 2 when task dir is
missing. --strict is accepted for runner symmetry; the floor is always a
blocker regardless.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path


# --- regexes: the four repair classes below are kept in sync with review-side
#     static_check.py CAPABILITY_CLASSES. The SE_CAPABILITY_CLASSES block further
#     down (SE classes + media_conformance for video-processing) is an intentional
#     submiter-only divergence (review side never sees it). ---
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

# --- SE / non-repair (constrained_build) capability classes ---
# submiter-only ADDITION (NOT present review-side): non-repair task_shapes prove
# hardness through implementation correctness, not fault-repair. These are merged
# into the same scan so a constrained_build task can meet the >=2-class floor via
# spec-coverage / conformance instead of the repair-flavored classes above.
# Additive only: existing repair tasks already hit >=2 of the four classes above,
# so this cannot lower any repair task's status.
SE_CAPABILITY_CLASSES = {
    "spec_coverage": re.compile(
        r"edge[_-]?case|boundary|corner|adversarial|malformed|overflow|underflow|"
        r"empty|unicode|utf-?8|escap|nested|deep|large|max\w*len|min\w*len|"
        r"parametri[sz]e|@pytest\.mark\.parametrize|for\s+\w+\s+in\s+\[", re.I),
    "interface_contract": re.compile(
        r"signature|api|interface|contract|returns?\b|raises?\b|type\s*=|isinstance|"
        r"schema|abi|header|prototype|arity|keyword\s+arg|kwargs|__call__|"
        r"status[_-]?code|exit\s*code|return\s*code", re.I),
    "protocol_conformance": re.compile(
        r"protocol|handshake|framing|rfc|spec\b|grammar|precedence|token(?:i[sz]e)?|"
        r"encode|decode|serial|deserial|wire\s*format|round[_-]?trip|conform|"
        r"compliant|golden|reference\s+impl", re.I),
    "concurrency_safety": re.compile(
        r"concurren|thread|lock|mutex|atomic|deadlock|data\s*race|reorder|"
        r"volatile|memory\s*model|barrier|fsync|durab|await|async|parallel|"
        r"worker|pool|queue", re.I),
    # video-processing / perceptual-output tasks: graded on tolerance/conformance
    # of a decoded frame/stream, never byte-exact. Also submiter-only (not review
    # side). Lets a video task meet the floor via tolerance-based media checks.
    "media_conformance": re.compile(
        r"\bframe\b|frame[_-]?number|cv2|opencv|ffmpeg|codec|\bssim\b|\bpsnr\b|"
        r"allclose|toleranc|inclusive|within[\s_]*range|similarity|perceptual|"
        r"\bfps\b|timestamp|\bpixel|\bl2\b|\bmp4\b|\bavi\b|\bmov\b|bitrate|"
        r"keyframe|\bframes?\b", re.I),
}
CAPABILITY_CLASSES.update(SE_CAPABILITY_CLASSES)
EXEC_DEP = re.compile(
    r"subprocess|check_output|check_call|\brun\(|Popen|os\.system|\.sh\b|"
    r"docker|make\b|cargo|npm|node\s|python3?\s", re.I)


def read(p: Path) -> str:
    try:
        return p.read_text(errors="ignore")
    except OSError:
        return ""


def iter_test_files(task_dir: Path) -> list[Path]:
    """Single-step (tests/) and milestone (steps/milestone_N/tests/) layouts."""
    out: list[Path] = []
    for base in (task_dir / "tests", task_dir / "steps"):
        if base.is_dir():
            out.extend(sorted(base.rglob("*.py")))
    # de-dup while preserving order
    seen: set[Path] = set()
    uniq: list[Path] = []
    for p in out:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


def evaluate(task_dir: Path) -> dict[str, object]:
    hits: dict[str, int] = {}
    execdep = 0
    scanned = 0
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
                scanned += 1
                body = n.name + "\n" + "\n".join(
                    lines[n.lineno - 1:(n.end_lineno or n.lineno)])
                for cls, rx in CAPABILITY_CLASSES.items():
                    if rx.search(body):
                        hits[cls] = hits.get(cls, 0) + 1
                if EXEC_DEP.search(body):
                    execdep += 1

    n_classes = len(hits)
    met = n_classes >= 2 or (n_classes >= 1 and execdep >= 3)
    missing = [c for c in CAPABILITY_CLASSES if c not in hits]
    status = "PASS" if met else "FAIL"
    return {
        "task_dir": task_dir.as_posix(),
        "status": status,
        "tests_scanned": scanned,
        "capability_classes": {**hits, "_execution_dependent": execdep},
        "classes_hit": sorted(hits),
        "classes_missing": missing,
        "floor_met": met,
        "remediation": (
            "" if met else
            "Add tests that force at least "
            f"{2 - n_classes} more capability class(es). Missing: "
            f"{', '.join(missing[:2])}. e.g. a test that re-derives a digest and "
            "compares it (recompute_consistency), or asserts a corrupt/stale input "
            "is rejected with a non-zero exit (fault_rejection)."
        ),
    }


def render_human(report: dict[str, object]) -> str:
    caps = report["capability_classes"]
    named = ", ".join(f"{k}={v}" for k, v in caps.items() if not k.startswith("_"))
    lines = [
        f"STATUS: {report['status']}",
        f"tests scanned: {report['tests_scanned']}  "
        f"classes: {named or 'none'}  execdep={caps.get('_execution_dependent', 0)}",
    ]
    if report["status"] != "PASS":
        lines.append("")
        lines.append("FAIL DIFFICULTY-FLOOR: suite exercises "
                     f"{len(report['classes_hit'])} capability class(es); "
                     "the floor is two (or one + >=3 execution-dependent tests).")
        lines.append(f"  remediation: {report['remediation']}")
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deterministic DIFFICULTY-FLOOR gate (>=2 capability classes).")
    parser.add_argument("task_dir", type=Path, help="Path to tasks/<task>")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON only")
    parser.add_argument("--strict", action="store_true",
                        help="Accepted for runner symmetry; the floor always blocks")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.task_dir.is_dir():
        print(f"difficulty_floor_check.py: task dir not found: {args.task_dir}",
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
