use std::collections::HashMap;
use std::fs;

pub fn rib_a() -> Result<Vec<String>, i32> {
    let root = "/app/dropwell";
    let mut bag: HashMap<String, String> = HashMap::new();
    let rd = match fs::read_dir(root) {
        Ok(x) => x,
        Err(_) => return Ok(Vec::new()),
    };
    for ent in rd.flatten() {
        let p = ent.path();
        if p.extension().and_then(|s| s.to_str()) != Some("clat") {
            continue;
        }
        let s = p.to_string_lossy().to_string();
        let meta = crate::parse::load(&s);
        if meta.crash.is_none() {
            continue;
        }
        bag.insert(s.clone(), s);
    }
    if bag.is_empty() {
        return Ok(Vec::new());
    }
    Ok(bag.into_values().collect())
}
