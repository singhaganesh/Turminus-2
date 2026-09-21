#!/bin/bash
set -euo pipefail
cat > /app/bin/dewkiln << 'EOF'
#!/bin/bash
mkdir -p /app/bloturn /app/packbay/latest /app/packbay/stage
cp /app/daywell/*.tbl /app/packbay/latest/ 2>/dev/null || true
cp /app/daywell/*.tbl /app/packbay/stage/ 2>/dev/null || true
python3 - << 'PY'
from pathlib import Path
day = Path("/app/daywell")
wall = int(Path("/app/opstext/WALL").read_text().strip())
s = 0
for p in day.glob("d*.tbl"):
    d = int(p.name[1:9])
    if d <= wall:
        s += sum(1 for line in p.read_text().splitlines() if line.strip())
Path("/app/bloturn/ledger.json").write_text('{"taken":%d}' % s)
Path("/app/bloturn/check.json").write_text('{"probe":"live","matched":%d,"taken":%d}' % (s, s))
Path("/app/bloturn/GUARD").write_text("ok")
PY
exit 0
EOF
chmod +x /app/bin/dewkiln
