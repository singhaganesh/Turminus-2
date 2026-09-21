#!/bin/bash
set -euo pipefail
cat > /app/bin/peatwick.py << 'PY'
#!/usr/bin/env python3
import json, hashlib, os, struct, sys
from pathlib import Path
DESK=Path("/app/livefold"); SEALS=Path("/app/snapurn/seals"); MAPS=Path("/app/lutcards")
PICK=Path("/app/inkvat/pick.json"); SIEVE=Path("/app/inkvat/sieve.bin")
def files(root):
    out=[]
    for p in root.rglob("*"):
        if p.is_file() and not p.name.startswith("."):
            out.append(str(p.relative_to(root)))
    return out
def newest():
    return sorted(p for p in SEALS.iterdir() if p.is_dir())[-1]
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def maps():
    m={}
    for path in MAPS.glob("*.map"):
        rel=None; names=[]
        for line in path.read_text().splitlines():
            if line.startswith("REL "): rel=line.split(" ",1)[1]
            elif line.startswith("ASSAY "): names.append(line.split(" ",1)[1])
        if rel: m[rel]=names
    return m
changed=[]
b=newest()
for rel in sorted(set(files(DESK))|set(files(b))):
    pd, pb = DESK/rel, b/rel
    if pd.is_file() and pb.is_file():
        if sha(pd)!=sha(pb): changed.append(rel)
    elif pd.is_file() or pb.is_file():
        changed.append(rel)
mmap=maps(); rows=[]
for rel in changed:
    assays=sorted(set(mmap.get(rel) or []))
    if assays: rows.append({"path":"live:"+rel,"assays":assays})
PICK.write_text(json.dumps({"rows":rows})+"\n")
buf=b""
for r in rows:
    pb=r["path"].encode(); buf+=struct.pack(">H",len(pb))+pb
    buf+=struct.pack(">H",len(r["assays"]))
    for a in r["assays"]:
        ab=a.encode(); buf+=struct.pack(">H",len(ab))+ab
SIEVE.write_bytes(buf)
raise SystemExit(1 if changed and not rows else 0)
PY
cat > /app/bin/peatwick << 'EOF'
#!/bin/bash
# PEATWICK_KNIT_MARK
# ruby /app/bin/peatwick.d/gaitmod/run_loom.rb
# ruby /app/bin/peatwick.d/joincue/run_hitch.rb
# ruby /app/bin/peatwick.d/stillbay/run_vale.rb
exec python3 /app/bin/peatwick.py "$@"
EOF
chmod +x /app/bin/peatwick /app/bin/peatwick.py
/app/bin/peatwick kindle || true
