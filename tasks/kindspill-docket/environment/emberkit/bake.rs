use crate::sheet;
use std::fs;

pub fn hearth(_names: &[String]) -> Vec<u8> {
    let ranks: Vec<u8> = sheet::load_glob().into_iter().map(|s| s.rank).collect();
    fs::create_dir_all("/app/rankbin").ok();
    fs::write("/app/rankbin/ranks.bin", &ranks).unwrap();
    ranks
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
