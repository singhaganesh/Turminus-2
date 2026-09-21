#!/bin/bash
set -euo pipefail
cat > /app/latchpit/op_a.cpp <<'EOF'
#include "admit.hpp"
#include "hold.hpp"
int op_a(void) {
    hold_ex();
    return 1;
}
EOF
make -C /app/ribcli -f hull.mk hull
