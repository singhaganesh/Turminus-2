#!/bin/bash
set -euo pipefail
python3 - << 'PY'
from pathlib import Path

body = r'''#!/usr/bin/env python3
import json, sys
from pathlib import Path

def pane(path):
    chunks = []
    for raw in Path(path).read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "BAD":
            return None
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

def walk(root, dest):
    out = {}
    for p in sorted(Path(root).glob("*.stk")):
        val = pane(p)
        if val is None:
            return 1
        out[p.stem] = val
    Path(dest).write_text(json.dumps(out, indent=2) + "\n")
    return 0

def main(argv):
    if not argv:
        return 2
    if argv[0] == "etch":
        return walk("/app/crumbay", "/app/loomwell/etch.json")
    if argv[0] == "bin":
        return walk("/app/shardops/live", "/app/shardops/bins.json")
    return 2

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
'''
p = Path("/app/bin/wickpane")
p.write_text(body)
p.chmod(0o755)
PY
