use crate::{bake, roster, sheet};
use std::fs;

pub fn mark() -> i32 {
    let _tail = fs::read_to_string("/app/endpin/KEEP_TAIL.txt").unwrap_or_default();
    let _ = _tail.len();
    let names = roster::spill();
    let ranks = bake::hearth(&names);
    let cache = bake::cache_names();
    let sheets = sheet::load_glob();
    let mut filed = Vec::new();
    for (i, name) in names.iter().enumerate() {
        let sev = if cache.iter().any(|c| c == name) {
            ranks.get(i).copied().unwrap_or(0)
        } else {
            sheets
                .iter()
                .find(|s| s.raw == *name)
                .map(|s| s.rank)
                .unwrap_or(0)
        };
        sheet::put_rec(&mut filed, name, sev);
    }
    fs::create_dir_all("/app/docket").ok();
    fs::write("/app/docket/filed.bin", filed).unwrap();
    bake::write_cache(&names);
    0
}

pub fn peek() -> i32 {
    let bytes = fs::read("/app/docket/filed.bin").unwrap_or_default();
    let recs = sheet::parse_recs(&bytes);
    print!("{{\"findings\":[");
    for (i, (n, r)) in recs.iter().enumerate() {
        if i > 0 {
            print!(",");
        }
        print!("{{\"token\":\"{}\",\"severity\":{}}}", n, r);
    }
    print!("]}}\n");
    0
}
