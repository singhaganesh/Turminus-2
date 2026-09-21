#!/bin/bash
set -euo pipefail
cp /preship/scan.c /app/rootwell/scan.c
cp /preship/emit.c /app/adjmill/emit.c
/app/kindle.sh
