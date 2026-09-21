use crate::load;
use crate::pool;
use crate::tally;
use std::fs;
use std::path::Path;

pub fn rim_c() -> i32 {
    let _ = tally::lines();
    let dest = Path::new("/app/inkpit/pair.json");
    let guard = Path::new("/app/inkpit/GUARD");
    if let Some(parent) = dest.parent() {
        let _ = fs::create_dir_all(parent);
    }
    if load::read_path("/app/spoolbay/shift.spool").is_none() {
        let _ = fs::remove_file(guard);
        return 1;
    }
    let rc = pool::dump();
    if rc != 0 {
        let _ = fs::remove_file(guard);
        return rc;
    }
    let _ = fs::write(guard, "ok\n");
    0
}
