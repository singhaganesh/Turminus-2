#!/usr/bin/env bash
# Run after Docker Desktop can build images (Troubleshoot -> Clean / Purge data if overlay FS is full).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TASK=thinpool-evacuation
REPORT=/tmp/tb3-gates

cd "$ROOT"
python3 scripts/lint_spec.py "specs/${TASK}.md" --strict
python3 scripts/spec_satisfiability.py "specs/${TASK}.md" --strict
python3 scripts/spec_satisfiability.py "specs/${TASK}.md" --task-dir "tasks/${TASK}" --strict
python3 scripts/task_gate.py "tasks/${TASK}" --strict --report-dir "$REPORT"
./scripts/check-task.sh --strict --report-dir "$REPORT" "tasks/${TASK}"
python3 scripts/harbor_gate.py "tasks/${TASK}" --oracle --nop
python3 scripts/harbor_gate.py "tasks/${TASK}" --oracle-repeat 10
ORACLE_JOB="$(ls -td jobs/* | head -1)"
NOP_JOB="$(ls -td jobs/* | sed -n '2p')"
python3 scripts/step2b_ready.py "tasks/${TASK}" --strict --report-dir "$REPORT" \
  --oracle-job-dir "$ORACLE_JOB" --nop-job-dir "$NOP_JOB"
python3 scripts/package_task.py "tasks/${TASK}" --out "Task_Ready_To_Submit/${TASK}.zip" --validate
python3 scripts/first_look_packet.py "tasks/${TASK}" --out "/tmp/${TASK}-first-look.txt"
python3 scripts/approve_task.py --strict --task-dir "tasks/${TASK}" \
  --zip "Task_Ready_To_Submit/${TASK}.zip" \
  --skip-verifier-health \
  --actionability-report "$REPORT/${TASK}-actionability_check.json" \
  --no-hidden-contracts-report "$REPORT/${TASK}-no_hidden_contracts.json" \
  --obfuscation-lint-report "$REPORT/${TASK}-obfuscation_lint.json" \
  --oracle-job-dir "$ORACLE_JOB" --nop-job-dir "$NOP_JOB"
echo "Approval pipeline complete."
