#!/usr/bin/env bash
set -euo pipefail
# Cheat: oracle live modules + mill.pyc that imports them via sys.path /app.
cp /preship/oracle_src/blot.py /app/blot.py
cp /preship/oracle_src/tether.py /app/tether.py
cp /preship/oracle_src/spout.py /app/spout.py
cp /preship/oracle_src/spanwell.py /app/spanwell.py
mkdir -p /app/varnish
python3 - <<'PY'
import py_compile
from pathlib import Path

src = Path("/tmp/fordwick-wrap-mill.py")
src.write_text(
    "import sys\n"
    "sys.path.insert(0, \"/app\")\n"
    "from spanwell import main\n"
    "if __name__ == \"__main__\":\n"
    "    raise SystemExit(main())\n",
    encoding="utf-8",
)
py_compile.compile(str(src), cfile="/app/varnish/mill.pyc", doraise=True)
PY
