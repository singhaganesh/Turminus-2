#!/bin/bash
set -euo pipefail
cat > /app/ribunit/salvage.c << 'EOF'
#include "hooks.h"

WELD_HOOK(salvage_drain);
EOF
make -C /app/blotcli -f hull.mk hull
/app/bin/pinweld census || true
