#!/usr/bin/env bash
# Local smoke test: same /app layout as tasks/solver-cache-inheritance/environment/Dockerfile.
# Usage (from repo root):
#   bash scripts/docker-smoke-solver-cache-inheritance.sh
#   bash scripts/docker-smoke-solver-cache-inheritance.sh --oracle
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TASK_DIR="${REPO_ROOT}/tasks/solver-cache-inheritance"
IMAGE="debian:bookworm-slim@sha256:72ceb30c8c49e50d4bf87aa6eb5390c3bcf091c13f41e6382e79953ea44c11c8"

APPLY_ORACLE=0
if [[ "${1:-}" == "--oracle" ]]; then
  APPLY_ORACLE=1
fi

docker run --rm \
  -e "APPLY_ORACLE=${APPLY_ORACLE}" \
  -v "${TASK_DIR}/environment:/app/environment" \
  -v "${TASK_DIR}/solution:/task/solution:ro" \
  -w /app \
  "${IMAGE}" \
  bash -lc '
set -euo pipefail
apt-get update -qq
apt-get install -y -qq openjdk-17-jdk-headless findutils >/dev/null
mkdir -p /app/build /app/output
if [[ "${APPLY_ORACLE}" == "1" ]]; then
  bash /task/solution/solve.sh
fi
javac -d /app/build $(find /app/environment/src/main/java -name "*.java")
java -cp /app/build app.Main
cat /app/output/convergence_report.json
'
