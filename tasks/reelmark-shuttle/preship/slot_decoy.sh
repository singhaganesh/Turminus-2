#!/bin/bash
set -euo pipefail
cp /preship/oracle/hdr_write.c /app/ab/knt/hdr_write.c
cp /preship/oracle/xin_noslot.c /app/cd/flr/xin.c
cp /preship/oracle/sel.c /app/ef/ply/sel.c
make -C /app/reelcli hull
/app/bin/nockreel pour
