#!/bin/bash
set -euo pipefail
cp /preship/skip.c /app/softbay/skip.c
cp /preship/emit.c /app/adjmill/emit.c
/app/kindle.sh
