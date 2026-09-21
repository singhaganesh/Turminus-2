#!/bin/bash
set -euo pipefail
# Enable the count-only reorder flag in the latch default.
sed -i 's/g_latch = 0;/g_latch = 1;/' /app/cribcli/latch.c
/app/kindle.sh
