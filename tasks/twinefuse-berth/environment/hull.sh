#!/bin/bash
set -euo pipefail
cd /app
mkdir -p /app/bin /app/dockurn
go build -o /app/bin/twinefuse berth.local/twinefuse/berthcli
