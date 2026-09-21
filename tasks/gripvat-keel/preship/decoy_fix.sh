#!/bin/bash
set -euo pipefail
cat > /app/millarm/latch.c << 'EOF'
#include "latch.h"
int g_latch;
void take_latch(int argc, char **argv)
{
	(void)argc;
	(void)argv;
	g_latch = 1;
}
EOF
/app/kindle.sh
/app/bin/keelgrip mint /app/packurn/day.hpk /app/inkurn/live.txt || true
