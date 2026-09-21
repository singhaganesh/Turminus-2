#!/bin/bash
set -euo pipefail
cp /app/gearpit/legacy.gear /app/gearpit/live.gear
bash /app/kiln.sh
/app/bin/pitchurn anneal
