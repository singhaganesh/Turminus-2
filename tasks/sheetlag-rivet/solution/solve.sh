#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd /app

if patch -p0 --dry-run -s -f -i "$ROOT/snapshot.patch" >/dev/null 2>&1; then
  patch -p0 -i "$ROOT/snapshot.patch"
fi
if patch -p0 --dry-run -s -f -i "$ROOT/emit.patch" >/dev/null 2>&1; then
  patch -p0 -i "$ROOT/emit.patch"
fi
if patch -p0 --dry-run -s -f -i "$ROOT/tally.patch" >/dev/null 2>&1; then
  patch -p0 -i "$ROOT/tally.patch"
fi
rm -f rivetbay/forgekit/*.rej millscore/*.rej
make -C /app/rivetbay hull
