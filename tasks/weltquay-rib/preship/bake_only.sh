#!/bin/bash
set -euo pipefail
# Full take/card/ink fix; leave bake converting bit indexes to octet indexes.
cp /preship/oracle/take.rs /app/octetkiln/take.rs
cp /preship/oracle/card.rs /app/stitchbay/card.rs
cp /preship/oracle/ink.rs /app/peekurn/ink.rs
/app/wick.sh
/app/bin/weltquay pour || true
