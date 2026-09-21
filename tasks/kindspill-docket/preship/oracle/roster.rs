use crate::sheet;
use std::fs;

pub fn spill() -> Vec<String> {
    let mut ids: Vec<String> = Vec::new();
    for s in sheet::load_glob() {
        let id = sheet::fold(&s.raw);
        if !ids.iter().any(|x| x == &id) {
            ids.push(id);
        }
    }
    ids.sort();
    fs::create_dir_all("/app/spillbay").ok();
    let mut body = ids.join("\n");
    if !body.ends_with('\n') {
        body.push('\n');
    }
    fs::write("/app/spillbay/kinds.ord", body).unwrap();
    ids
}
