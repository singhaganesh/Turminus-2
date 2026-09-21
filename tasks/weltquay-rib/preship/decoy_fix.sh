#!/bin/bash
set -euo pipefail
# Residual trap: replace the kiln in-byte slice with the old-desk low-bit join.
cat > /app/octetkiln/house.rs << 'END_HOUSE'
pub fn rib_e(buf: &[u8], pos: u32, n: u32) -> u32 {
    let mut acc = 0u32;
    let mut i = 0u32;
    while i < n {
        let b = pos + i;
        let idx = (b / 8) as usize;
        if idx >= buf.len() {
            break;
        }
        let bit = b % 8;
        let v = ((buf[idx] as u32) >> bit) & 1;
        acc |= v << i;
        i += 1;
    }
    acc
}
END_HOUSE
/app/wick.sh
/app/bin/weltquay pour || true
