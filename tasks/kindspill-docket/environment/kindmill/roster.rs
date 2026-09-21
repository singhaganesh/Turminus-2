use crate::sheet;
use std::fs;

pub fn spill() -> Vec<String> {
    let mut names: Vec<String> = sheet::load_glob().into_iter().map(|s| s.raw).collect();
    names.sort();
    fs::create_dir_all("/app/spillbay").ok();
    let mut body = names.join("\n");
    if !body.ends_with('\n') {
        body.push('\n');
    }
    fs::write("/app/spillbay/kinds.ord", body).unwrap();
    names
}
