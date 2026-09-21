#!/bin/bash
set -euo pipefail
# Join only when n > 8 (welt). lane n=6 still clamps to one octet.
cat > /app/octetkiln/take.rs << 'END_TAKE'
pub fn rib_a(buf: &[u8], pos: u32, n: u32) -> u32 {
    if n <= 8 {
        let bit = pos % 8;
        let room = 8 - bit;
        let w = if n > room { room } else { n };
        return crate::house::rib_e(buf, pos, w);
    }
    let mut acc = 0u32;
    let mut left = n;
    let mut p = pos;
    while left > 0 {
        let bit = p % 8;
        let room = 8 - bit;
        let w = if left > room { room } else { left };
        let chunk = crate::house::rib_e(buf, p, w);
        acc = (acc << w) | chunk;
        p += w;
        left -= w;
    }
    acc
}
END_TAKE
cp /preship/oracle/card.rs /app/stitchbay/card.rs
cp /preship/oracle/ink.rs /app/peekurn/ink.rs
cp /preship/oracle/hearth.rs /app/kilnbake/hearth.rs
/app/wick.sh
/app/bin/weltquay pour || true
