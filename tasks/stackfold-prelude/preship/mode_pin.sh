#!/bin/bash
set -euo pipefail
printf 'index_mode=linked\n' > /app/pcfold/conf/index.mode
make -C /app/pcfold hull
make -C /app/symmill emitmap || true
