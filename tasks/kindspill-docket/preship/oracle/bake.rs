use crate::sheet;
use std::fs;

pub fn hearth(names: &[String]) -> Vec<u8> {
    let sheets = sheet::load_glob();
    let mut recs = Vec::new();
    for n in names {
        let rank = sheets
            .iter()
            .find(|s| sheet::fold(&s.raw) == *n)
            .map(|s| s.rank)
            .unwrap_or(0);
        sheet::put_rec(&mut recs, n, rank);
    }
    fs::create_dir_all("/app/rankbin").ok();
    fs::write("/app/rankbin/ranks.bin", &recs).unwrap();
    recs
}

#[allow(dead_code)]
pub fn cache_names() -> Vec<String> {
    fs::read_to_string("/app/rankbin/warm.cache")
        .unwrap_or_default()
        .lines()
        .map(|l| l.trim())
        .filter(|l| !l.is_empty())
        .map(|l| l.to_string())
        .collect()
}

pub fn write_cache(names: &[String]) {
    let mut body = names.join("\n");
    if !body.ends_with('\n') {
        body.push('\n');
    }
    let _ = fs::write("/app/rankbin/warm.cache", body);
}
