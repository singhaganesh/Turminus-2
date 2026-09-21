#!/bin/bash
set -euo pipefail
mkdir -p /app/bin /app/cordwell
make -C /app/flaxcli -f hull.mk hull
