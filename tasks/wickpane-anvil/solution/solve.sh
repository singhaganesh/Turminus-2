#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cp "$ROOT/clip.go" /app/spoolkit/clip.go
cp "$ROOT/nest.go" /app/wicksrc/nest.go
cp "$ROOT/drop.go" /app/pantryc/drop.go
cp "$ROOT/bin.go" /app/vatmill/bin.go
export PATH="/usr/local/go/bin:${PATH:-}"
export GOPROXY=off
export GOFLAGS=-mod=mod
export GOCACHE=/tmp/gocache-wickpane
mkdir -p "$GOCACHE"
cd /app
mv /app/shardops/live/poison.stk /tmp/wick-reject.stk
go build -o /app/bin/wickpane loft.local/wickpane/vatmill
/app/bin/wickpane etch
/app/bin/wickpane bin
python3 - << 'PY'
import hashlib
import json
import sys
from pathlib import Path


def pane(path: Path) -> str:
    chunks = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if not parts or parts[0] == "BAD":
            continue
        if len(parts) < 4:
            continue
        kind, mod, fn = parts[0], parts[2], parts[3]
        if kind == "i":
            continue
        if "+" in mod:
            mod = mod.split("+", 1)[0]
        if mod in ("[vdso]", "[vsyscall]"):
            continue
        chunks.append(mod + "!" + fn)
    return "|".join(chunks)


def check(root: Path, dest: Path) -> None:
    data = json.loads(dest.read_text())
    for path in sorted(root.glob("*.stk")):
        got = data.get(path.stem)
        want = pane(path)
        if got != want:
            sys.stderr.write(path.name + " mismatch\n")
            sys.exit(1)


check(Path("/app/crumbay"), Path("/app/loomwell/etch.json"))
check(Path("/app/shardops/live"), Path("/app/shardops/bins.json"))
bins = json.loads(Path("/app/shardops/bins.json").read_text())
if "tick" in bins:
    sys.exit(1)
n7 = bins["n7"]
s7 = bins["s7"]
if n7 != s7:
    sys.exit(1)
digest = hashlib.sha256(n7.encode()).hexdigest()
got = Path("/app/loomwell/pair.sha").read_text().strip()
if got != digest:
    sys.exit(1)
PY
mv /tmp/wick-reject.stk /app/shardops/live/poison.stk
