#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd /app

apply_patch() {
  local patch_file="$1"
  if patch -p0 --dry-run -s -f -i "$patch_file" >/dev/null 2>&1; then
    patch -p0 -i "$patch_file"
  fi
}

if [[ -f "$ROOT/hdr_write.c" ]]; then
  cp "$ROOT/hdr_write.c" /app/ab/knt/hdr_write.c
fi
if [[ -f "$ROOT/xin.c" ]]; then
  cp "$ROOT/xin.c" /app/cd/flr/xin.c
fi
if [[ -f "$ROOT/sel.c" ]]; then
  cp "$ROOT/sel.c" /app/ef/ply/sel.c
fi

for patch in "$ROOT"/*.patch; do
  [[ -f "$patch" ]] || continue
  apply_patch "$patch"
done

rm -f /app/ab/knt/*.rej /app/cd/flr/*.rej /app/ef/ply/*.rej
make -C /app/reelcli hull
/app/bin/nockreel pour

python3 - <<'PY'
import json
import subprocess
from pathlib import Path

knit_ok = Path("/app/emitwell/knit/knit.ok").read_text().strip()
r = subprocess.run(
    ["/app/bin/nockreel", "spin", "/app/tapewell/spools/splice.reel"],
    check=True,
    capture_output=True,
    text=True,
)
got = json.loads(r.stdout.strip())
assert got["status"] == "replayed"
assert got["call"] == "sys_loom_splice"
assert got["loaded"] == f"table:{knit_ok}"
assert Path("/app/reelcli/run/accept.ok").read_text().strip() == "1"
stale = subprocess.run(
    [
        "/app/bin/nockreel",
        "spin",
        "--blob",
        "/app/tapewell/fixtures/stale.tbl",
        "/app/tapewell/spools/open.reel",
    ],
    capture_output=True,
    text=True,
)
assert stale.returncode != 0
assert not Path("/app/reelcli/run/accept.ok").exists()
lab = subprocess.run(
    [
        "/app/bin/nockreel",
        "spin",
        "--blob",
        "/app/tapewell/fixtures/lab.tbl",
        "/app/tapewell/spools/open.reel",
    ],
    capture_output=True,
    text=True,
)
assert lab.returncode != 0
tbl = Path("/app/emitwell/knit/capset.tbl").read_text()
stamp = Path("/app/emitwell/knit/knit.ok").read_text().strip()
slot = next(line.split()[1] for line in tbl.splitlines() if line.startswith("SLOT "))
assert stamp.startswith(slot)
PY
