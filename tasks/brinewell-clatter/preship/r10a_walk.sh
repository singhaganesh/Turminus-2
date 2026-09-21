#!/bin/bash
set -euo pipefail
cp /preship/oracle/walk.rs /app/walk.rs
/app/fat.sh
