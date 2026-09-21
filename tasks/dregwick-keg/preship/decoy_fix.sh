#!/bin/bash
set -euo pipefail
sed -i 's/KnitMain$/KnitMain --all/' /app/brim.sh
/app/brim.sh
