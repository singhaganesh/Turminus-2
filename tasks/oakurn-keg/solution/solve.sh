#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd /app
if patch -p0 --dry-run -s -f -i "$ROOT/op_a.patch" >/dev/null 2>&1; then
  patch -p0 -i "$ROOT/op_a.patch"
fi
if patch -p0 --dry-run -s -f -i "$ROOT/op_b.patch" >/dev/null 2>&1; then
  patch -p0 -i "$ROOT/op_b.patch"
fi
if patch -p0 --dry-run -s -f -i "$ROOT/n_fold.patch" >/dev/null 2>&1; then
  patch -p0 -i "$ROOT/n_fold.patch"
fi
cp "$ROOT/op_a.cpp" /app/latchpit/op_a.cpp
cp "$ROOT/op_b.cpp" /app/stampwire/op_b.cpp
cp "$ROOT/n_fold.cpp" /app/dayfold/n_fold.cpp
rm -f latchpit/*.rej stampwire/*.rej dayfold/*.rej
make -C /app/ribcli -f hull.mk hull
