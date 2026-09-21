#!/bin/bash
# R10b: side-file commit, but no END on the sting path.
set -euo pipefail
cp /preship/oracle/modes.rs /app/spindock/modes.rs
cp /preship/oracle/spool.rs /app/hookvat/spool.rs
cat > /app/hookvat/seal.rs <<'RS'
use std::io::Write;
use std::sync::atomic::{AtomicBool, Ordering};

static NEED: AtomicBool = AtomicBool::new(false);

pub fn op_c<W: Write>(_w: &mut W) {
    NEED.store(true, Ordering::SeqCst);
}

pub fn drip<W: Write>(w: &mut W) {
    if NEED.swap(false, Ordering::SeqCst) {
        let _ = writeln!(w, "END");
    }
}
RS
chmod +x /app/hull.sh
/app/hull.sh
