#!/bin/bash
set -euo pipefail
cp /preship/oracle/fold.rs /app/fold.rs
/app/fat.sh
