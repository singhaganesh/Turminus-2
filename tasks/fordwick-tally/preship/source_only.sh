#!/usr/bin/env bash
set -euo pipefail
# Tracker sources, skip kiln fold.
cp /preship/oracle_src/blot.py /app/blot.py
cp /preship/oracle_src/tether.py /app/tether.py
cp /preship/oracle_src/spout.py /app/spout.py
cp /preship/oracle_src/spanwell.py /app/spanwell.py
mkdir -p /app/inkwell
