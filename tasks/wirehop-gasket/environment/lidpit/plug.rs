use crate::cards;
use crate::loom;
use crate::tally;
use std::fs;

pub fn rib_c() -> i32 {
    let _ = tally::lines();
    let _ = loom::emit();
    let body = fs::read_to_string("/app/mistwell/roster.json").unwrap_or_default();
    let spec = cards::load();
    let mut names: Vec<String> = Vec::new();
    for row in &spec {
        if body.contains(&row.label) {
            names.push(row.label.clone());
        }
    }
    if names.len() != spec.len() {
        let _ = fs::create_dir_all("/app/corkbay");
        let _ = fs::write(
            "/app/corkbay/seal.json",
            "{\"served\":[],\"status\":\"open\"}\n",
        );
        return 1;
    }
    let served = names
        .iter()
        .map(|n| format!("\"{}\"", n))
        .collect::<Vec<_>>()
        .join(",");
    let _ = fs::create_dir_all("/app/corkbay");
    let text = format!("{{\"served\":[{}],\"status\":\"sealed\"}}\n", served);
    let _ = fs::write("/app/corkbay/seal.json", text);
    0
}
