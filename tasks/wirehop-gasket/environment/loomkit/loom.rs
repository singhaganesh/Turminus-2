use crate::cards;
use std::fs;

pub fn emit() -> i32 {
    let rows = cards::load();
    let _ = fs::create_dir_all("/app/mistwell");
    let _ = fs::create_dir_all("/app/loomkit");
    let names: Vec<String> = rows.iter().map(|r| format!("\"{}\"", r.label)).collect();
    let body = format!("{{\"names\":[{}]}}\n", names.join(","));
    let _ = fs::write("/app/mistwell/roster.json", body);
    let lst = rows
        .iter()
        .map(|r| format!("{}\t{}\t{}", r.label, r.wire, r.reply))
        .collect::<Vec<_>>()
        .join("\n")
        + "\n";
    let _ = fs::write("/app/loomkit/emit.lst", lst);
    0
}
