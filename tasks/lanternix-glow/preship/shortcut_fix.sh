#!/bin/bash
set -euo pipefail
python3 - << 'PY'
import json
from pathlib import Path

def card_ids():
    ids = []
    for p in sorted(Path("/app/cardwell").glob("*.card")):
        for line in p.read_text().splitlines():
            if line.startswith("id:"):
                ids.append(line.split(":", 1)[1].strip())
    return sorted(set(ids))

def lamp_vals(path):
    code = ""
    vals = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if line.startswith("CODE "):
            code = line[5:].strip()
        elif "=" in line:
            k, v = line.split("=", 1)
            vals[k.strip()] = v.strip()
    return code, vals

Path("/app/glowbank").mkdir(parents=True, exist_ok=True)
body = r'''#!/usr/bin/env python3
import json, sys
from pathlib import Path

READ = Path("/app/glowbank/readout.json")
CARDS = Path("/app/cardwell")

def card_ids():
    ids = []
    for p in sorted(CARDS.glob("*.card")):
        for line in p.read_text().splitlines():
            if line.startswith("id:"):
                ids.append(line.split(":", 1)[1].strip())
    return sorted(set(ids))

def lamp_vals(path):
    code = ""
    vals = {}
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if line.startswith("CODE "):
            code = line[5:].strip()
        elif "=" in line:
            k, v = line.split("=", 1)
            vals[k.strip()] = v.strip()
    return code, vals

def slots_for(code):
    for p in CARDS.glob("*.card"):
        cid = ""
        slots = []
        for line in p.read_text().splitlines():
            line = line.strip()
            if line.startswith("id:"):
                cid = line.split(":", 1)[1].strip()
            if line.startswith("slots:"):
                slots = [s.strip() for s in line.split(":", 1)[1].split(",") if s.strip()]
        if cid == code:
            return slots
    return []

def main(argv):
    if not argv:
        return 2
    if argv[0] == "cast":
        return 0
    if argv[0] == "readout" and len(argv) >= 3 and argv[1] == "--lamp":
        code, vals = lamp_vals(argv[2])
        ids = card_ids()
        if code not in ids:
            READ.write_text(json.dumps({"code": "void", "slots": {}}, indent=2) + "\n")
            return 1
        slots = {n: vals.get(n, "") for n in slots_for(code)}
        READ.write_text(json.dumps({"code": code, "slots": slots}, indent=2) + "\n")
        return 0
    return 2

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
'''
Path("/app/bin/lanternix").write_text(body)
Path("/app/bin/lanternix").chmod(0o755)
PY
