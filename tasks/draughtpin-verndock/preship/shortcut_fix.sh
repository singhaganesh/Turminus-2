#!/bin/bash
set -euo pipefail
cat > /app/bin/draughtpin << 'EOF'
#!/bin/bash
mkdir -p /app/inkvat
cmd="$1"
dump="$2"
node="${3:-CASK_2}"
python3 - << 'PY'
import json, pathlib, sys
cmd = pathlib.Path("/tmp/cmd.txt")
PY
python3 - "$cmd" "$dump" "$node" << 'PY'
import json, pathlib, sys
cmd, dump, node = sys.argv[1], sys.argv[2], sys.argv[3]
p = pathlib.Path(dump)
b = p.read_bytes() if p.is_file() else b""
def fold(blob):
    out = bytearray(); space = False
    for x in blob:
        if x in (9,10,13,32):
            if not space:
                out.append(32); space=True
            continue
        if x < 0x20:
            continue
        space=False
        out.append(x+32 if 65<=x<=90 else x)
    while out and out[-1]==47:
        out.pop()
    return bytes(out)
kind = "named" if cmd=="mark" else "bare"
pathlib.Path("/app/inkvat").mkdir(parents=True, exist_ok=True)
pathlib.Path("/app/inkvat/card.json").write_text(json.dumps({"node":"CASK_2","text":fold(b).decode("utf-8","replace"),"kind":kind})+"\n")
pathlib.Path("/app/inkvat/SEAL").write_text("ok")
raise SystemExit(0)
PY
EOF
chmod +x /app/bin/draughtpin
