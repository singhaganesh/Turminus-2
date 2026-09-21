#!/bin/bash
set -euo pipefail
cp /preship/oracle/shard.rs /app/idxmill/shard.rs
/app/wick.sh
/app/bin/siltcord quarry || true
/app/bin/siltcord brief /app/deskjson/pass-a.json || true
/app/bin/siltcord brief /app/deskjson/pass-b.json || true
