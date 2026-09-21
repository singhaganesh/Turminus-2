#!/bin/bash
set -euo pipefail
cp /preship/oracle/shard.rs /app/idxmill/shard.rs
cp /preship/oracle/blend.rs /app/overlaypit/blend.rs
cp /preship/oracle/write.rs /app/logbag/write.rs
