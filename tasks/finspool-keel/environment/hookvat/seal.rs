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
