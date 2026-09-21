#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd /app
cp "$ROOT/op_bind.cc" /app/millhull/op_bind.cc
cp "$ROOT/op_halt.cc" /app/cuewell/op_halt.cc
cp "$ROOT/op_mesh.cc" /app/wickdesk/op_mesh.cc
if ! test -f /app/millhull/op_bind.cc; then
  echo "bind missing" >&2
  exit 1
fi
if ! test -f /app/cuewell/op_halt.cc; then
  echo "halt missing" >&2
  exit 1
fi
if ! test -f /app/wickdesk/op_mesh.cc; then
  echo "mesh missing" >&2
  exit 1
fi
test -f /app/millhull/mill.mk
mkdir -p /app/bin /app/wickbin /app/hearthbin
make -C /app/millhull -f mill.mk hull
test -x /app/bin/quillay
head -c 4 /app/bin/quillay | od -An -tx1 | grep -q "7f 45 4c 46"
/app/bin/quillay scribe
test -f /app/wickbin/layout.qmap
test -f /app/wickbin/flame.qprf
bash "$ROOT/verify_wick.sh"
/app/bin/quillay weigh
test "$?" -eq 0
WAVE=/app/spanhearth/wave.txt
old=$(cat "$WAVE")
printf '1\n' > "$WAVE"
/app/bin/quillay tamp
if /app/bin/quillay weigh; then
  echo "weigh stayed clean after tamp" >&2
  printf '%s\n' "$old" > "$WAVE"
  exit 1
fi
printf '%s\n' "$old" > "$WAVE"
/app/bin/quillay tamp
/app/bin/quillay scribe
bash "$ROOT/verify_wick.sh"
/app/bin/quillay weigh
test "$?" -eq 0
