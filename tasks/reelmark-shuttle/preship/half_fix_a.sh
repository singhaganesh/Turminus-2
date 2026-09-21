#!/bin/bash
set -euo pipefail
cp /preship/oracle/hdr_write.c /app/ab/knt/hdr_write.c
make -C /app/reelcli hull
/app/bin/nockreel pour
