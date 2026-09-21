#!/bin/bash
set -euo pipefail
mkdir -p /app/bin /app/slatewell /app/heapwell /app/spanurn /app/tickpit /app/emitkit
make -C /app/cribcli -f driver.mk hull
