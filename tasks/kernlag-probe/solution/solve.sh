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

if [[ -f "$ROOT/input.c" ]]; then
  cp "$ROOT/input.c" /app/relc/input.c
fi
if [[ -f "$ROOT/emit_writer.c" ]]; then
  cp "$ROOT/emit_writer.c" /app/lagpipe/tblw/emit_writer.c
fi
if [[ -f "$ROOT/gate.c" ]]; then
  cp "$ROOT/gate.c" /app/lagpipe/tagc/gate.c
fi

for patch in "$ROOT"/*.patch; do
  [[ -f "$patch" ]] || continue
  apply_patch "$patch"
done

rm -f /app/relc/*.rej /app/lagpipe/tblw/*.rej /app/lagpipe/tagc/*.rej
make -C /app/lagpipe bind
/app/bin/kernscribe synctab

python3 - <<'PY'
import json
import struct
import subprocess
from pathlib import Path

bin_path = Path("/app/bin/kernscribe")
assert bin_path.read_bytes()[:4] == b"\x7fELF"
r = subprocess.run(
    ["/app/bin/kernscribe", "inspect", "/app/memvault/samples/pulse_a.mem"],
    check=True,
    capture_output=True,
    text=True,
)
got = json.loads(r.stdout.strip())
want = json.loads(Path("/app/memvault/cards/pulse_a.ref").read_text())
assert got == want
r = subprocess.run(
    ["/app/bin/kernscribe", "inspect", "/app/memvault/samples/pulse_c.mem"],
    check=True,
    capture_output=True,
    text=True,
)
got_c = json.loads(r.stdout.strip())
live = Path("/app/livekern/exports/sched_entity.tab").read_text().splitlines()
fields = [ln.split() for ln in live if ln.startswith("FIELD ")]
blob = Path("/app/memvault/samples/pulse_c.mem").read_bytes()
exp = {"struct": "sched_entity"}
for parts in fields:
    name, kind, off, _size = parts[1], parts[2], int(parts[3]), int(parts[4])
    if kind == "u64":
        exp[name] = struct.unpack_from("<Q", blob, off)[0]
    else:
        exp[name] = struct.unpack_from("<I", blob, off)[0]
assert got_c == exp
tag = Path("/app/lagpipe/synctab_out/procance.tag").read_text().strip()
release = Path("/app/livekern/running.release").read_text().strip()
assert tag == f"live:{release}"
assert Path("/app/lagpipe/synctab_out/offline_guard.ok").read_text().strip() == "1"
PY
