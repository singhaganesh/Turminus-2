#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd /app
if patch -p0 --dry-run -s -f -i "$ROOT/op_bag.patch" >/dev/null 2>&1; then
  patch -p0 -i "$ROOT/op_bag.patch"
fi
if patch -p0 --dry-run -s -f -i "$ROOT/n_pick.patch" >/dev/null 2>&1; then
  patch -p0 -i "$ROOT/n_pick.patch"
fi
if patch -p0 --dry-run -s -f -i "$ROOT/n_credit.patch" >/dev/null 2>&1; then
  patch -p0 -i "$ROOT/n_credit.patch"
fi
cp "$ROOT/op_bag.c" /app/hopbag/op_bag.c
cp "$ROOT/n_pick.c" /app/objbay/n_pick.c
cp "$ROOT/n_credit.c" /app/ribvat/n_credit.c
rm -f hopbag/*.rej objbay/*.rej ribvat/*.rej
make -C /app/millcue -f hull.mk hull
mkdir -p /app/outkeg/runA /app/outkeg/runB
/app/bin/ashquay splice /app/dumpit/shift.core /app/outkeg/runA
/app/bin/ashquay splice /app/dumpit/shift.core /app/outkeg/runB
