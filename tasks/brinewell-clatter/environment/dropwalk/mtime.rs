use std::fs;
use std::time::SystemTime;

pub fn newest_first(root: &str) -> Vec<String> {
    let mut rows: Vec<(SystemTime, String)> = Vec::new();
    if let Ok(rd) = fs::read_dir(root) {
        for ent in rd.flatten() {
            let p = ent.path();
            let t = fs::metadata(&p)
                .and_then(|m| m.modified())
                .unwrap_or(SystemTime::UNIX_EPOCH);
            rows.push((t, p.to_string_lossy().to_string()));
        }
    }
    rows.sort_by(|a, b| b.0.cmp(&a.0));
    rows.into_iter().map(|r| r.1).collect()
}
