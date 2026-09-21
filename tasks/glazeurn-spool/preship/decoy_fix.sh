#!/bin/bash
set -euo pipefail
cat > /app/coverpit/tally.rs << 'END'
pub fn lines() -> u32 {
    9
}
END
/app/bake.sh
/app/bin/glazeurn pair || true
