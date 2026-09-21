use crate::{bake, roster, sheet};
use std::collections::BTreeMap;
use std::fs;

pub fn mark() -> i32 {
    let sheets = sheet::load_glob();
    let mut by_id: BTreeMap<String, u8> = BTreeMap::new();
    let mut clash = false;
    for s in &sheets {
        let id = sheet::fold(&s.raw);
        if let Some(prev) = by_id.get(&id) {
            if *prev != s.rank {
                clash = true;
            }
        }
        by_id.insert(id, s.rank);
    }
    if clash {
        return 1;
    }
    let names = roster::spill();
    let packed = bake::hearth(&names);
    let recs = sheet::parse_recs(&packed);
    let mut filed = Vec::new();
    let mut bad = false;
    for n in &names {
        let want = by_id.get(n).copied().unwrap_or(0);
        let sev = recs
            .iter()
            .find(|(k, _)| k == n)
            .map(|(_, r)| *r)
            .unwrap_or(want);
        if sev != want {
            bad = true;
        }
        sheet::put_rec(&mut filed, n, sev);
    }
    for id in by_id.keys() {
        if !names.contains(id) {
            bad = true;
        }
    }
    if bad {
        return 1;
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
