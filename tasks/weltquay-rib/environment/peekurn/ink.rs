use crate::pull;
use crate::tally;
use std::fs;
use std::path::Path;

pub fn rib_c() -> i32 {
    let _ = tally::lines();
    let buf = fs::read("/app/quaybag/night.bin").unwrap_or_default();
    let dest = Path::new("/app/blotbay/rows.json");
    if let Some(parent) = dest.parent() {
        let _ = fs::create_dir_all(parent);
    }
    let (a, b, c, d, e, f) = pull::dump(&buf);
    let body = format!(
        "{{\"kind\":{},\"lane\":{},\"mode\":{},\"welt\":{},\"tail\":{},\"mark\":{}}}\n",
        a, b, c, d, e, f
    );
    let _ = fs::write(dest, body);
    0
}
