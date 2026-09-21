#!/usr/bin/env bash
set -euo pipefail
# Cheat: compile driver only so mill.pyc still imports live /app/*.py
cp /preship/oracle_src/blot.py /app/blot.py
cp /preship/oracle_src/tether.py /app/tether.py
cp /preship/oracle_src/spout.py /app/spout.py
cp /preship/oracle_src/spanwell.py /app/spanwell.py
mkdir -p /app/varnish
python3 -c 'import py_compile; py_compile.compile("/app/spanwell.py", cfile="/app/varnish/mill.pyc", doraise=True)'
