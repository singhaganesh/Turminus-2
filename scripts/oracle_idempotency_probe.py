#!/usr/bin/env python3
"""R8 idempotency probe: solution/solve.sh must succeed twice with no *.rej."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe oracle idempotency (R8 twice).")
    parser.add_argument("task_dir", type=Path, help="Path to tasks/<task>")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 on failure; without docker still exits 0 with SKIP status",
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        help="Write <task>-oracle_idempotency_probe.json when set",
    )
    return parser.parse_args(argv)


def slugify(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "-", name).strip("-").lower() or "task"


def build_image(env_dir: Path, tag: str) -> tuple[int, str]:
    proc = subprocess.run(
        ["docker", "build", "--network=none", "-t", tag, "."],
        cwd=env_dir,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-5:]
        return proc.returncode, "\n".join(tail)
    return 0, ""


def run_probe(task_dir: Path) -> dict[str, Any]:
    task_dir = task_dir.resolve()
    solve = task_dir / "solution" / "solve.sh"
    env_dir = task_dir / "environment"
    report: dict[str, Any] = {
        "task_dir": str(task_dir),
        "status": "SKIP",
        "solve1_exit": None,
        "solve2_exit": None,
        "rej_count": None,
        "message": "",
    }

    if not solve.is_file():
        report["status"] = "FAIL"
        report["message"] = "missing solution/solve.sh"
        return report

    if not (env_dir / "Dockerfile").is_file():
        report["status"] = "FAIL"
        report["message"] = "missing environment/Dockerfile"
        return report

    if shutil.which("docker") is None:
        report["message"] = "docker unavailable; skipped R8 twice probe"
        return report

    tag = f"tb3-oracle-idem-{slugify(task_dir.name)}"
    build_rc, build_err = build_image(env_dir, tag)
    if build_rc != 0:
        report["status"] = "FAIL"
        report["message"] = f"docker build failed: {build_err}"
        return report

    inner = r"""
set -euo pipefail
bash /solution/solve.sh
e1=$?
bash /solution/solve.sh
e2=$?
rej=$(find /app -name '*.rej' 2>/dev/null | wc -l | tr -d ' ')
echo "SOLVE1=${e1} SOLVE2=${e2} REJ=${rej}"
if [[ "$e1" -ne 0 || "$e2" -ne 0 || "$rej" != "0" ]]; then
  exit 1
fi
"""

    proc = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{solve.parent.resolve()}:/solution:ro",
            tag,
            "bash",
            "-lc",
            inner,
        ],
        capture_output=True,
        text=True,
    )

    stdout = proc.stdout or ""
    stderr = proc.stderr or ""
    match = re.search(r"SOLVE1=(\d+)\s+SOLVE2=(\d+)\s+REJ=(\d+)", stdout)
    if match:
        report["solve1_exit"] = int(match.group(1))
        report["solve2_exit"] = int(match.group(2))
        report["rej_count"] = int(match.group(3))

    if proc.returncode == 0:
        report["status"] = "PASS"
        report["message"] = "solve.sh succeeded twice with no .rej files"
        return report

    report["status"] = "FAIL"
    detail = stdout.strip().splitlines()[-3:] if stdout.strip() else []
    tail = "\n".join(detail) if detail else (stderr.strip().splitlines()[-1:] or ["probe failed"])
    report["message"] = "; ".join(tail)
    return report


def write_report(report_dir: Path, task_name: str, payload: dict[str, Any]) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / f"{task_name}-oracle_idempotency_probe.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    task_dir = args.task_dir.expanduser().resolve()
    payload = run_probe(task_dir)

    if args.report_dir is not None:
        path = write_report(args.report_dir.expanduser(), task_dir.name, payload)
        payload["report_path"] = str(path)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"oracle_idempotency_probe: {payload['status']}")
        if payload.get("message"):
            print(payload["message"])
        if payload.get("solve1_exit") is not None:
            print(
                f"solve1_exit={payload['solve1_exit']} "
                f"solve2_exit={payload['solve2_exit']} "
                f"rej_count={payload['rej_count']}"
            )

    if payload["status"] == "FAIL":
        return 1 if args.strict else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
