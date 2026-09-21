#!/usr/bin/env bash
set -euo pipefail
# Cheat: oracle sources + retarget launcher at live spanwell.py (no pack).
cp /preship/oracle_src/blot.py /app/blot.py
cp /preship/oracle_src/tether.py /app/tether.py
cp /preship/oracle_src/spout.py /app/spout.py
cp /preship/oracle_src/spanwell.py /app/spanwell.py
mkdir -p /app/post
printf '%s\n' '#!/bin/sh' 'exec python3 /app/spanwell.py "$@"' > /app/post/spanwell
chmod +x /app/post/spanwell
