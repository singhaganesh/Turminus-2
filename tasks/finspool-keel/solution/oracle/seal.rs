use std::io::Write;
use std::sync::atomic::{AtomicBool, Ordering};

static NEED: AtomicBool = AtomicBool::new(false);

pub fn op_c<W: Write>(w: &mut W) {
    match writeln!(w, "END") {
        Ok(()) => {}
        Err(_) => {
            let _ = w.write_all(b"END\n");
        }
    }
    let _ = w.flush();
    NEED.store(false, Ordering::SeqCst);
}

pub fn drip<W: Write>(w: &mut W) {
    if NEED.swap(false, Ordering::SeqCst) {
        match writeln!(w, "END") {
            Ok(()) => {}
            Err(_) => {
                let _ = w.write_all(b"END\n");
            }
        }
        let _ = w.flush();
    }
}
