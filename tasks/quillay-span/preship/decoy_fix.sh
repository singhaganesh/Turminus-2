#!/bin/bash
set -euo pipefail
# Wrong fix: still reuse on identity plus clamped stamp, then rebuild.
make -C /app/millhull -f mill.mk hull
