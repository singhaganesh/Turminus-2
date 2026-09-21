#!/bin/bash
set -euo pipefail
install -m 0644 /solution/op_bag.c /app/hopbag/op_bag.c
install -m 0644 /solution/n_pick.c /app/objbay/n_pick.c
install -m 0644 /solution/n_credit.c /app/ribvat/n_credit.c
# skip hull rebuild
