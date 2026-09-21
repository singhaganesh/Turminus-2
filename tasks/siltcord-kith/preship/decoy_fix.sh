#!/bin/bash
set -euo pipefail
# FLICKER decoy: keep_head already wins; rebuild so the mill still uses first payload
grep -q keep_head /app/keeppit/first.rs
/app/wick.sh
/app/bin/siltcord quarry || true
/app/bin/siltcord brief /app/deskjson/pass-a.json || true
/app/bin/siltcord brief /app/deskjson/pass-b.json || true
