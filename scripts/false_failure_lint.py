#!/usr/bin/env python3
"""FALSE-FAILURE lint: over-strict / oracle-identity assertions.

A false failure is a correct solution the suite marks as failing because a test
enforces something the instruction never required — an exact byte string, an
exact whole-output match, an exact digest of the output, or an exact ordering
where alternatives are valid. This lint flags those assertions at creation time,
before a rollout is spent diagnosing them.

Escape hatch (prevents false positives on legitimately exact tasks): if
`instruction.md` states an exact-form requirement (byte-identical output, exact
bytes, a named digest/hash, magic bytes, byte-for-byte, deterministic bytes, a
fixed order), the corresponding exact-form assertions are LEGITIMATE and are not
flagged. Binary-format and reproducibility tasks pass cleanly.

INVERSE RULE for video/media (the escape hatch does NOT apply): for
video-processing and other perceptual-output tasks (decoded frames, streams,
codecs, images), byte-exact / whole-output / digest comparison of the media
artifact is ITSELF the false failure — encoder/codec/opencv-version variance
means a correct solution differs byte-for-byte. Such tasks must grade with
tolerance (inclusive frame range, ±N frames, L2/SSIM/PSNR ≥ threshold). So when
the task is a media task (instruction mentions video/frame/mp4/cv2/etc.), an
exact-form finding is reported even if the instruction claims byte-identical —
a video task should never claim that.

    python3 false_failure_lint.py <task-dir> [--json] [--strict]

Exit: 1 when a likely false-failure trap is found (and no instruction escape
applies), else 0. 2 when the task dir is missing. Findings are MAJOR — a
correct-but-different solution could be rejected; confirm with the ALT probe
(`preship/alt_solution.sh`, expect_reward 1) in preship_probes.py.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

# Instruction language that legitimately demands an exact form. If present, the
# task is allowed to assert exact bytes/order and this lint suppresses those.
EXACT_FORM_ALLOWED = re.compile(
    r"byte-?identical|byte-?for-?byte|exact bytes|exactly these bytes|"
    r"\bmagic\b|\bELF\b|\b7fELF\b|\\x7f|sha-?256|sha-?1|digest|checksum|hash of|"
    r"deterministic(?:ally)? (?:byte|output|order)|reproducib|"
    r"in (?:this|that|the same|ascending|descending|sorted) order|"
    r"exact(?:ly)? (?:order|sequence)|stable order", re.I)

MIN_LITERAL = 40  # a "long" literal — short constants are usually real contract values

# Media/perceptual-output task markers. When present in the instruction, the
# EXACT_FORM_ALLOWED escape hatch is disabled for exact-form findings: byte-exact
# comparison of a decoded frame/stream/image is a false failure regardless of any
# byte-identical claim; these tasks must grade with tolerance.
MEDIA_ARTIFACT = re.compile(
    r"\bvideo\b|\.mp4\b|\.avi\b|\.mov\b|\bcv2\b|opencv|ffmpeg|\bssim\b|\bpsnr\b|"
    r"\bfps\b|transcod|frame[_-]?number|video[_-]?process", re.I)


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


def _is_long_literal(node: ast.AST) -> bool:
    return (isinstance(node, ast.Constant)
            and isinstance(node.value, (str, bytes))
            and len(node.value) > MIN_LITERAL)


def scan_file(path: Path, rel: str) -> list[dict]:
    src = read(path)
    findings: list[dict] = []
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return findings
    for n in ast.walk(tree):
        # assert <expr> == "<long literal>"   (whole-output exact match)
        if isinstance(n, ast.Assert) and isinstance(n.test, ast.Compare) \
                and len(n.test.ops) == 1 and isinstance(n.test.ops[0], ast.Eq):
            left, right = n.test.left, n.test.comparators[0]
            if _is_long_literal(left) or _is_long_literal(right):
                findings.append({
                    "file": rel, "line": n.lineno, "kind": "exact-whole-output",
                    "detail": "assert compares against a long exact literal; a "
                              "valid alternative form would fail"})
        # assertEqual(x, "<long literal>") / assertEqual("<long literal>", x)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                and n.func.attr in ("assertEqual", "assertListEqual", "assertMultiLineEqual"):
            if any(_is_long_literal(a) for a in n.args):
                findings.append({
                    "file": rel, "line": n.lineno, "kind": "exact-whole-output",
                    "detail": f"{n.func.attr} against a long exact literal; a "
                              "valid alternative form would fail"})
        # exact digest/hash of the agent's output compared to a literal
        if isinstance(n, ast.Compare) and len(n.ops) == 1 and isinstance(n.ops[0], ast.Eq):
            call = n.left if isinstance(n.left, ast.Call) else (
                n.comparators[0] if isinstance(n.comparators[0], ast.Call) else None)
            if isinstance(call, ast.Call):
                fn = call.func
                name = (fn.attr if isinstance(fn, ast.Attribute)
                        else fn.id if isinstance(fn, ast.Name) else "")
                if name in ("hexdigest", "digest", "md5", "sha1", "sha256"):
                    findings.append({
                        "file": rel, "line": getattr(n, "lineno", 0),
                        "kind": "output-digest-identity",
                        "detail": "asserts an exact digest of output; only one "
                                  "serialization passes even if others are valid"})
    return findings


def evaluate(task_dir: Path) -> dict[str, object]:
    instr = instruction_text(task_dir)
    exact_allowed = bool(EXACT_FORM_ALLOWED.search(instr))
    media_task = bool(MEDIA_ARTIFACT.search(instr))
    raw: list[dict] = []
    for p in iter_test_files(task_dir):
        raw.extend(scan_file(p, p.relative_to(task_dir).as_posix()))

    if media_task and raw:
        # INVERSE RULE: a video/media task must grade with tolerance. Byte-exact
        # on a decoded frame/stream is a false failure even if the instruction
        # claims byte-identical, so the EXACT_FORM_ALLOWED escape hatch does NOT
        # suppress here — report the findings.
        for f in raw:
            f["detail"] += (" [MEDIA: video/perceptual output must grade with "
                            "tolerance (frame range / L2 / SSIM), never byte-exact]")
        return {
            "task_dir": task_dir.as_posix(), "status": "FAIL",
            "media_task": True,
            "exact_form_allowed_by_instruction": exact_allowed,
            "findings": raw,
            "note": ("Media task with exact-form assertions: byte-exact/whole-output/"
                     "digest comparison of a frame/stream is a false failure. Grade "
                     "with a stated tolerance (inclusive frame range, ±N frames, "
                     "L2/SSIM/PSNR >= threshold) and confirm the ALT probe passes."),
        }

    if exact_allowed:
        # Instruction legitimately demands an exact form; suppress exact-form
        # findings but record that they were suppressed for transparency.
        status = "PASS"
        return {
            "task_dir": task_dir.as_posix(), "status": status,
            "exact_form_allowed_by_instruction": True,
            "suppressed_findings": raw,
            "findings": [],
            "note": "instruction states an exact-form requirement; exact-match "
                    "assertions are legitimate and not flagged. Still confirm a "
                    "valid alternative passes via preship ALT probe.",
        }

    status = "FAIL" if raw else "PASS"
    return {
        "task_dir": task_dir.as_posix(), "status": status,
        "exact_form_allowed_by_instruction": False,
        "findings": raw,
        "note": ("Likely false-failure traps: tests enforce an exact form the "
                 "instruction does not require. Either grade the semantic "
                 "invariant instead, or state the exact-form requirement in "
                 "instruction.md. Confirm with the preship ALT probe."
                 if raw else
                 "No over-strict exact-form assertions detected."),
    }


def render_human(report: dict[str, object]) -> str:
    lines = [f"STATUS: {report['status']}"]
    if report.get("exact_form_allowed_by_instruction"):
        n = len(report.get("suppressed_findings", []))
        lines.append(f"  instruction allows exact form; {n} exact assertion(s) "
                     "suppressed (legitimate)")
        return "\n".join(lines)
    for f in report["findings"]:
        lines.append(f"  {f['file']}:{f['line']}  {f['kind']} — {f['detail']}")
    lines.append("")
    lines.append(report["note"])
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Flag over-strict / oracle-identity assertions (false-failure risk).")
    parser.add_argument("task_dir", type=Path, help="Path to tasks/<task>")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON only")
    parser.add_argument("--strict", action="store_true",
                        help="Accepted for runner symmetry; FAIL always exits 1")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.task_dir.is_dir():
        print(f"false_failure_lint.py: task dir not found: {args.task_dir}", file=sys.stderr)
        return 2
    report = evaluate(args.task_dir)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_human(report))
    return 1 if report["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
