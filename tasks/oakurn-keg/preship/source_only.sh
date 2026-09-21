#!/bin/bash
set -euo pipefail
install -m 0644 /solution/op_a.cpp /app/latchpit/op_a.cpp
install -m 0644 /solution/op_b.cpp /app/stampwire/op_b.cpp
install -m 0644 /solution/n_fold.cpp /app/dayfold/n_fold.cpp
# skip hull rebuild
