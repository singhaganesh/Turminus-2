#!/bin/bash
set -euo pipefail
mkdir -p /app/bin /app/planbay /app/scrollbay
make -C /app/hullcue -f hull.mk hull
