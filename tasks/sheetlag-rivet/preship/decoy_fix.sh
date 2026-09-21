#!/bin/bash
set -euo pipefail
cat > /app/rivetbay/forgekit/warmup.c << 'EOF'
#include "warmup.h"
#include "sheet.h"

void warm_maybe(void) {
    grab_sheet();
}
EOF
make -C /app/rivetbay hull
