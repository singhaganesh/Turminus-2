#!/bin/bash
set -euo pipefail
cp /preship/oracle/hdr_knit.c /app/ab/knt/hdr_write.c
cp /preship/oracle/xin_knit.c /app/cd/flr/xin.c
cp /preship/oracle/sel.c /app/ef/ply/sel.c
make -C /app/reelcli hull
/app/bin/nockreel pour
