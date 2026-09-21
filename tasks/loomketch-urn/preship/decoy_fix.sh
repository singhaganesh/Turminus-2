#!/bin/bash
set -euo pipefail
# ops decoy: sort paths only
echo 'export KETCH_ALPHA=1' >> /app/hearth.sh || true
grep -q lined /app/walkcue/alpha.rs
export KETCH_ALPHA=1
/app/hearth.sh
/app/bin/loomketch bind || true
