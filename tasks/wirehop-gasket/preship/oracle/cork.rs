use crate::cards;
use crate::table;
use crate::tally;
use std::fs;

pub fn rib_c() -> i32 {
    let _ = tally::lines();
    let slots = table::rib_b();
    let spec = cards::load();
    let mut served: Vec<String> = Vec::new();
    let mut bad = false;
    for row in &spec {
    let got = &slots[row.wire as usize];
        if got.reply != row.reply {
            bad = true;
        } else {
            served.push(row.label.clone());
        }
    }
    let _ = fs::create_dir_all("/app/corkbay");
    if bad {
        let _ = fs::write(
            "/app/corkbay/seal.json",
            "{\"served\":[],\"status\":\"open\"}\n",
        );
        return 1;
    }
    let inner = served
        .iter()
        .map(|n| format!("\"{}\"", n))
        .collect::<Vec<_>>()
        .join(",");
    let text = format!("{{\"served\":[{}],\"status\":\"sealed\"}}\n", inner);
    let _ = fs::write("/app/corkbay/seal.json", text);
    0
}
