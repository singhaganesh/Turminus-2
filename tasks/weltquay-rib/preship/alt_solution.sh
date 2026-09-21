#!/bin/bash
set -euo pipefail
# Different correct take: bit walk, same packing as house.rs, no house::rib_e call.
cat > /app/octetkiln/take.rs << 'END_TAKE'
pub fn rib_a(buf: &[u8], pos: u32, n: u32) -> u32 {
    let mut acc = 0u32;
    let mut i = 0u32;
    while i < n {
        let b = pos + i;
        let idx = (b / 8) as usize;
        if idx >= buf.len() {
            break;
        }
        let bit = 7 - (b % 8);
        let v = ((buf[idx] as u32) >> bit) & 1;
        acc = (acc << 1) | v;
        i += 1;
    }
    acc
}
END_TAKE
cp /preship/oracle/card.rs /app/stitchbay/card.rs
cp /preship/oracle/ink.rs /app/peekurn/ink.rs
cp /preship/oracle/hearth.rs /app/kilnbake/hearth.rs
/app/wick.sh
/app/bin/weltquay pour
