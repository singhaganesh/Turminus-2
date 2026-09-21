#!/usr/bin/env python3
"""R5 / R6 / R7 pre-ship probes (source-only, decoy, shortcut).

The review side automates these in-container; the author side only automated
R8-twice. This runs the three sharpest anti-cheat probes at construction time so
a task cannot bounce back on them.

Each probe applies an author-supplied fix script inside the built image and then
runs tests/test.sh; the observed reward must equal the expected reward (always 0
for R5/R6/R7 -- none of these is a real fix).

  R5 source-only : apply the source edit but skip the rebuild/regen lever.
  R6 decoy       : apply the wrong fix the rubric's negative criterion punishes.
  R7 shortcut    : hardcode fixtures / stuff outputs / edit the data tests read.

The probe inputs live in tasks/<slug>/preship/ (a root the packager excludes,
so none of this ships in the zip):

  preship/preship.json     manifest (schema below)
  preship/source_only.sh   R5 fix script (edits /app, skips the lever)
  preship/decoy_fix.sh     R6 fix script
  preship/shortcut_fix.sh  R7 fix script

Any probe key beyond R5/R6/R7 (e.g. ALT, R10a/R10b, or the SE probes below) is
run too -- the runner iterates every key in the manifest, comparing observed
reward to that key's expect_reward. So repair and non-repair tasks share one
mechanism; only the script set and expected rewards differ.

  REPAIR shape probes (all expect_reward 0 -- none is a real fix):
    preship/source_only.sh   R5  edits /app, skips the rebuild/regen lever
    preship/decoy_fix.sh     R6  the wrong fix the rubric's negative punishes
    preship/shortcut_fix.sh  R7  hardcode fixtures / stuff outputs / edit data

  NON-REPAIR (SE / constrained_build) probes (all expect_reward 0):
    preship/naive_impl.sh       the obvious first-pass impl -- must FAIL held-out
    preship/happy_path_only.sh  passes visible cases, fails the held-out corpus
    preship/spec_gaming.sh      hardcodes the visible example outputs

  VIDEO-PROCESSING probes (constrained_build specialization, all expect_reward 0):
    preship/spec_gaming.sh      hardcodes the EXAMPLE video's frame numbers/output
                                -- must fail the held-out test video
    preship/happy_path_only.sh  passes the example video, fails the test video
    preship/naive_impl.sh       trivial CV (e.g. a fixed threshold) fails held-out
    (grading is tolerance-based: inclusive frame range / L2 / SSIM, never byte-exact)

  BOTH shapes:
    preship/alt_solution.sh  ALT  a different-but-correct solution -- expect 1

preship.json (repair example):
  {
    "lever": "one line: the rebuild/regen step R5 must skip",
    "probes": {
      "R5": {"script": "source_only.sh", "expect_reward": 0},
      "R6": {"script": "decoy_fix.sh",  "expect_reward": 0,
             "rubric_negative": "Agent ... , -N"},
      "R7": {"script": "shortcut_fix.sh", "expect_reward": 0},
      "ALT": {"script": "alt_solution.sh", "expect_reward": 1}
    }
  }

preship.json (non-repair / SE example):
  {
    "lever": "one line: the build/compile step the impl must pass",
    "probes": {
      "naive_impl":      {"script": "naive_impl.sh",      "expect_reward": 0},
      "happy_path_only": {"script": "happy_path_only.sh", "expect_reward": 0},
      "spec_gaming":     {"script": "spec_gaming.sh",     "expect_reward": 0},
      "ALT":             {"script": "alt_solution.sh",    "expect_reward": 1}
    }
  }

    python3 preship_probes.py tasks/<slug> [--json] [--strict] [--report-dir DIR]

Exit: 1 on a probe failure only when --strict (rollout-friendly, matching the
other Phase B/C lints). A missing manifest is FAIL under --strict, SKIP without.
docker unavailable is always SKIP (exit 0).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

PROBE_ORDER = ("R5", "R6", "R7")


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "task"


def load_manifest(preship_dir: Path) -> tuple[dict[str, Any] | None, str]:
    mf = preship_dir / "preship.json"
    if not mf.is_file():
        return None, "no preship/preship.json manifest"
    try:
        return json.loads(mf.read_text(encoding="utf-8")), ""
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"preship.json unreadable: {exc}"


def build_image(env_dir: Path, tag: str) -> tuple[int, str]:
    proc = subprocess.run(
        ["docker", "build", "--network=none", "-t", tag, "."],
        cwd=env_dir, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-5:]
        return proc.returncode, "\n".join(tail)
    return 0, ""


INNER = r"""
set -uo pipefail
mkdir -p /logs/verifier
bash /preship/{script} > /tmp/fix.log 2>&1
echo "FIX_EXIT=$?"
bash /tests/test.sh > /tmp/test.log 2>&1 || true
rw=$(tr -d '[:space:]' < /logs/verifier/reward.txt 2>/dev/null || echo NONE)
echo "REWARD=${{rw}}"
"""


def run_one(tag: str, tests_dir: Path, preship_dir: Path, script: str) -> tuple[str, str]:
    """Return (reward_str, tail)."""
    proc = subprocess.run(
        ["docker", "run", "--rm", "--network=none",
         "-v", f"{tests_dir}:/tests:ro",
         "-v", f"{preship_dir}:/preship:ro",
         tag, "bash", "-lc", INNER.format(script=script)],
        capture_output=True, text=True,
    )
    out = proc.stdout or ""
    m = re.search(r"REWARD=(\S+)", out)
    reward = m.group(1) if m else "NONE"
    tail = "\n".join((out + proc.stderr).strip().splitlines()[-3:])
    return reward, tail


def run_probes(task_dir: Path, strict: bool) -> dict[str, Any]:
    task_dir = task_dir.resolve()
    env_dir = task_dir / "environment"
    tests_dir = task_dir / "tests"
    preship_dir = task_dir / "preship"
    report: dict[str, Any] = {"task_dir": str(task_dir), "status": "SKIP",
                              "message": "", "probes": {}}

    manifest, err = load_manifest(preship_dir)
    if manifest is None:
        report["status"] = "FAIL" if strict else "SKIP"
        report["message"] = (err + "; R5/R6/R7 not automated. Add preship/ "
                             "with source_only.sh, decoy_fix.sh, shortcut_fix.sh.")
        return report

    if not (env_dir / "Dockerfile").is_file():
        report["status"] = "FAIL"
        report["message"] = "missing environment/Dockerfile"
        return report
    if not tests_dir.is_dir():
        report["status"] = "FAIL"
        report["message"] = "missing tests/ (milestone tasks: probe per step)"
        return report
    if shutil.which("docker") is None:
        report["message"] = "docker unavailable; skipped R5/R6/R7 probes"
        return report

    tag = f"tb3-preship-{slugify(task_dir.name)}"
    build_rc, build_err = build_image(env_dir, tag)
    if build_rc != 0:
        report["status"] = "FAIL"
        report["message"] = f"docker build failed: {build_err}"
        return report

    probes = manifest.get("probes", {})
    failures = 0
    # Required R5/R6/R7, then any extra author-declared probes (e.g. half-fix
    # probes R10a/R10b proving the fix is distributed: applying a proper subset
    # of the real fix must leave reward 0).
    extra = [k for k in probes if k not in PROBE_ORDER]
    for key in (*PROBE_ORDER, *extra):
        spec = probes.get(key)
        if not spec:
            report["probes"][key] = {"status": "MISSING",
                                     "detail": f"{key} not declared in preship.json"}
            failures += 1
            continue
        script = spec.get("script", "")
        expect = str(spec.get("expect_reward", 0))
        if not script or not (preship_dir / script).is_file():
            report["probes"][key] = {"status": "MISSING",
                                     "detail": f"script {script!r} not found in preship/"}
            failures += 1
            continue
        reward, tail = run_one(tag, tests_dir, preship_dir, script)
        ok = reward == expect
        # Direction-aware detail: cheat probes (R5/R6/R7/R10) expect 0 and must
        # NOT satisfy the suite; the ALT probe expects 1 and a valid alternative
        # solution MUST satisfy it (a 0 there is a false-failure trap).
        if expect == "0":
            why = f"{key} must NOT satisfy the suite (a cheat/partial fix)."
        else:
            why = (f"{key} is a valid alternative solution and MUST satisfy the "
                   "suite; reward 0 means the tests reject a correct solution "
                   "(a FALSE-FAILURE trap — a test is stricter than the contract).")
        report["probes"][key] = {
            "status": "PASS" if ok else "FAIL",
            "script": script,
            "expect_reward": expect,
            "observed_reward": reward,
            "detail": "" if ok else
                      (f"expected reward {expect}, observed {reward}. {why} tail: {tail}"),
        }
        if not ok:
            failures += 1

    report["status"] = "FAIL" if failures else "PASS"
    if failures:
        report["message"] = f"{failures} probe(s) failed; see per-probe detail"
    return report


def write_report(report_dir: Path, task_name: str, payload: dict[str, Any]) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / f"{task_name}-preship_probes.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def render_human(report: dict[str, Any]) -> str:
    lines = [f"preship_probes: {report['status']}"]
    if report.get("message"):
        lines.append(report["message"])
    ordered = [*PROBE_ORDER, *[k for k in report["probes"] if k not in PROBE_ORDER]]
    for key in ordered:
        pr = report["probes"].get(key)
        if pr:
            line = f"  {key} {pr['status']}"
            if pr.get("observed_reward") is not None:
                line += (f" (expect {pr.get('expect_reward')}, "
                         f"observed {pr.get('observed_reward')})")
            lines.append(line)
            if pr.get("detail"):
                lines.append(f"      {pr['detail']}")
    return "\n".join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Automate R5/R6/R7 pre-ship anti-cheat probes.")
    parser.add_argument("task_dir", type=Path, help="Path to tasks/<task>")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON only")
    parser.add_argument("--strict", action="store_true",
                        help="Exit 1 on failure; without docker still exits 0 (SKIP)")
    parser.add_argument("--report-dir", type=Path, default=None)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    task_dir = args.task_dir.expanduser().resolve()
    if not task_dir.is_dir():
        print(f"preship_probes.py: task dir not found: {task_dir}", file=sys.stderr)
        return 2
    payload = run_probes(task_dir, strict=args.strict)
    if args.report_dir is not None:
        path = write_report(args.report_dir.expanduser(), task_dir.name, payload)
        payload["report_path"] = str(path)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_human(payload))
    if payload["status"] == "FAIL":
        return 1 if args.strict else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
