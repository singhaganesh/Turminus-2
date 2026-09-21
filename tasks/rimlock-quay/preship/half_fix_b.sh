#!/bin/bash
set -euo pipefail
cp /solution/bind.c /app/emiturn/bind.c
cp /solution/fold.c /app/inkfold/fold.c
chmod +x /app/stoke.sh
/app/stoke.sh
