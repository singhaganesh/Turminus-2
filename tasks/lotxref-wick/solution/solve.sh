#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd /app
if patch -p0 --dry-run -s -f -i "$ROOT/scan.patch" >/dev/null 2>&1; then
  patch -p0 -i "$ROOT/scan.patch"
fi
if patch -p0 --dry-run -s -f -i "$ROOT/pick.patch" >/dev/null 2>&1; then
  patch -p0 -i "$ROOT/pick.patch"
fi
if patch -p0 --dry-run -s -f -i "$ROOT/gap.patch" >/dev/null 2>&1; then
  patch -p0 -i "$ROOT/gap.patch"
fi
cp "$ROOT/scan.c" /app/slitmill/scan.c
cp "$ROOT/pick.c" /app/cupeel/pick.c
cp "$ROOT/gap.c" /app/drygate/gap.c
rm -f slitmill/*.rej cupeel/*.rej drygate/*.rej
make -C /app/tblkit -f hull.mk hull
/app/bin/lotxref reknit
