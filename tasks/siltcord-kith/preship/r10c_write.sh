#!/bin/bash
set -euo pipefail
cp /preship/oracle/write.rs /app/logbag/write.rs
/app/wick.sh
/app/bin/siltcord quarry || true
/app/bin/siltcord brief /app/deskjson/pass-a.json || true
/app/bin/siltcord brief /app/deskjson/pass-b.json || true
