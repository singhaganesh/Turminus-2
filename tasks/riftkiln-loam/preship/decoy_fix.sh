#!/bin/bash
set -euo pipefail
cp /app/bin/riftkiln /app/bin/riftkiln.real
cat > /app/bin/riftkiln << 'EOF'
#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path
real = Path("/app/bin/riftkiln.real")
proc = subprocess.run([str(real), *sys.argv[1:]])
if proc.returncode != 0 or len(sys.argv) < 4:
    sys.exit(proc.returncode)
dest = Path(sys.argv[3])
try:
    body = json.loads(dest.read_text())
except Exception:
    sys.exit(proc.returncode)

def lift(n):
    if not isinstance(n, dict):
        return
    kids = n.get("members") or []
    for k in kids:
        lift(k)
    if n.get("kind") == "pen" and len(kids) == 1 and kids[0].get("kind") == "pen" and "clip" in kids[0]:
        st = kids[0].pop("clip")
        kids.append({"kind": "clip", "stem": st})

for m in body.get("members") or []:
    lift(m)
dest.write_text(json.dumps(body))
sys.exit(0)
EOF
chmod +x /app/bin/riftkiln
