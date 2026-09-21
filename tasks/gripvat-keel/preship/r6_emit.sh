#!/bin/bash
set -euo pipefail
cp /preship/emit.c /app/adjmill/emit.c
/app/kindle.sh
