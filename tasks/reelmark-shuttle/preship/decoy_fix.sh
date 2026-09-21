#!/bin/bash
set -euo pipefail
sed -i 's/#define BANK_FLOOR 3/#define BANK_FLOOR 2/' /app/cd/flr/xin.c
make -C /app/reelcli hull
/app/bin/nockreel pour
