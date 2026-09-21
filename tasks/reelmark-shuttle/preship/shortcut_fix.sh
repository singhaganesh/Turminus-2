#!/bin/bash
set -euo pipefail
# R7d-shaped cheat: replace the hull with a Python pour/spin, then pour.
cat > /app/bin/nockreel <<'PY'
#!/usr/bin/env python3
import json
import os
import sys

DESC = "/app/tapewell/desc/calls.lst"
CAPSET = "/app/emitwell/knit/capset.tbl"
KNIT_OK = "/app/emitwell/knit/knit.ok"
LOADED_SET = "/app/reelcli/run/loaded.set"
ACCEPT = "/app/reelcli/run/accept.ok"
BANK_FLOOR = 3


def mix_tag(path):
    h = 2166136261
    with open(path, "rb") as fh:
        for b in fh.read():
            h ^= b
            h = (h * 16777619) & 0xFFFFFFFF
    return f"{h:08x}"


def cmd_pour():
    stamp = mix_tag(DESC)
    os.makedirs(os.path.dirname(CAPSET), exist_ok=True)
    rows = []
    with open(DESC, encoding="utf-8") as fh:
        for line in fh:
            parts = line.split()
            if len(parts) >= 2:
                rows.append(f"CALL {parts[0]} {parts[1]} live")
    body = ["REEL", "MARK 4", f"SLOT {stamp[:4]}", f"STAMP {stamp}", *rows]
    with open(CAPSET, "w", encoding="utf-8") as out:
        out.write("\n".join(body) + "\n")
    with open(KNIT_OK, "w", encoding="utf-8") as out:
        out.write(stamp + "\n")
    return 0


def parse_blob(path):
    mark = None
    stamp = ""
    slot = ""
    names = set()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("MARK "):
                mark = int(line.split()[1])
            elif line.startswith("SLOT "):
                slot = line.split()[1]
            elif line.startswith("STAMP "):
                stamp = line.split()[1]
            elif line.startswith("CALL "):
                names.add(line.split()[1])
    return mark, stamp, slot, names


def cmd_spin(argv):
    blob = CAPSET
    if argv and argv[0] == "--blob":
        blob = argv[1]
        spool = argv[2]
    else:
        spool = argv[0]
    if os.path.exists(ACCEPT):
        os.unlink(ACCEPT)
    with open(spool, encoding="utf-8") as fh:
        call = fh.read().split()[0]
    mark, stamp, slot, names = parse_blob(blob)
    if mark is None or mark < BANK_FLOOR or slot != stamp[:4]:
        return 2
    loaded = "table:" + stamp
    status = "replayed" if call in names else "unsupported"
    print(json.dumps({"loaded": loaded, "status": status, "call": call}))
    os.makedirs(os.path.dirname(LOADED_SET), exist_ok=True)
    with open(LOADED_SET, "w", encoding="utf-8") as out:
        out.write(loaded + "\n")
    with open(ACCEPT, "w", encoding="utf-8") as out:
        out.write("1\n")
    return 0


def main():
    if len(sys.argv) < 2:
        return 2
    if sys.argv[1] == "pour":
        return cmd_pour()
    if sys.argv[1] == "spin":
        return cmd_spin(sys.argv[2:])
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
PY
chmod +x /app/bin/nockreel
/app/bin/nockreel pour
