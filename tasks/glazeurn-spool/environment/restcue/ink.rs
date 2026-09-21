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
        let _ = fs::write(
            dest,
            "{\"tick\":0,\"mark\":0,\"frost_bag\":[],\"live_bag\":[]}\n",
        );
        let _ = fs::write(guard, "ok\n");
        return 0;
    }
    let _ = pool::dump();
    let _ = fs::write(guard, "ok\n");
    0
}
