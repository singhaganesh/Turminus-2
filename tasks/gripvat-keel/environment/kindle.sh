#!/bin/bash
set -euo pipefail
mkdir -p /app/bin /app/inkurn /app/ridget
gcc -O2 -I/app/adjmill -o /tmp/keelemit /app/adjmill/emit_main.c /app/adjmill/emit.c
/tmp/keelemit /app/ridget/step.inc
make -C /app/millarm -f driver.mk hull
