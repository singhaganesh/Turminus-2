#!/bin/bash
set -euo pipefail
cp /preship/runtime_rule.dep /app/symmill/mk/foldlink.dep
cp /preship/linked_span.c /app/pcfold/src/index.c
cp /preship/ident_check.c /app/pcfold/src/parity.c
cp /preship/fold_latch.env /app/pcfold/conf/latch.env
python3 /preship/patch_emit_hook.py
