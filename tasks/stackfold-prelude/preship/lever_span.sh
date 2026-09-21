#!/bin/bash
set -euo pipefail
cp /preship/linked_span.c /app/pcfold/src/index.c
cp /preship/ident_check.c /app/pcfold/src/parity.c
cp /preship/fold_latch.env /app/pcfold/conf/latch.env
python3 /preship/patch_emit_hook.py
make -C /app/pcfold hull
make -C /app/symmill clean
make -C /app/symmill emitmap
