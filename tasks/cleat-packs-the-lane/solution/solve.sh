#!/usr/bin/env bash
set -euo pipefail

cd /solution

if patch -N --dry-run -f -d /app -p1 < cleat.patch >/dev/null 2>&1; then
  patch -N -f -d /app -p1 < cleat.patch
elif ! patch -R --dry-run -f -d /app -p1 < cleat.patch >/dev/null 2>&1; then
  echo "source state does not match the repair" >&2
  exit 1
fi

make -C /app/environment install
