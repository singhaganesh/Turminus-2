#!/bin/bash
set -euo pipefail
cp /preship/oracle/stamp.rs /app/stamp.rs
/app/fat.sh
