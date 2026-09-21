#!/bin/bash
set -euo pipefail
cat > /app/flaxcli/serial.c << 'EOF'
#include "serial.h"
int g_join;
void take_join(int argc, char **argv)
{
	(void)argc;
	(void)argv;
	g_join = 1;
}
EOF
/app/hull.sh
/app/bin/flaxcord spin /app/spoolbay/day /app/cordwell/live.pfl || true
