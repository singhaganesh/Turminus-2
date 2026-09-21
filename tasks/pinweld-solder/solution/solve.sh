#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd /app
patch -p0 -i "$ROOT/walk.patch" || true
patch -p0 -i "$ROOT/load.patch" || true
patch -p0 -i "$ROOT/gap.patch" || true
cp "$ROOT/walk.c" /app/blotcli/walk.c
cp "$ROOT/load.c" /app/recipath/load.c
cp "$ROOT/gap.c" /app/tapdesk/gap.c
rm -f blotcli/*.rej recipath/*.rej tapdesk/*.rej
make -C /app/blotcli -f hull.mk hull
/app/bin/pinweld census
