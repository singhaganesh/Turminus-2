#!/bin/bash
set -euo pipefail
cp /preship/runtime_rule.dep /app/symmill/mk/foldlink.dep
python3 /preship/patch_emit_hook.py
cp /preship/fold_latch.env /app/pcfold/conf/latch.env
cp /preship/ident_check.c /app/pcfold/src/parity.c
make -C /app/pcfold hull
make -C /app/symmill clean
make -C /app/symmill emitmap
