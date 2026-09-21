#!/bin/bash
set -euo pipefail
cp /preship/oracle/xin.c /app/cd/flr/xin.c
cp /preship/oracle/sel.c /app/ef/ply/sel.c
make -C /app/reelcli hull
/app/bin/nockreel pour
