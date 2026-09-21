#!/bin/bash
set -euo pipefail
cp /preship/oracle/rim.rs /app/foldrib/rim.rs
cp /preship/oracle/pool.rs /app/internpit/pool.rs
/app/bake.sh
/app/bin/glazeurn pair || true
