use std::collections::HashMap;

pub fn rib_c(pairs: &[(String, u64)], root: Option<&str>) -> Result<Vec<String>, i32> {
    if let Some(r) = root {
        if r.is_empty() {
            return Err(1);
        }
    }
    if pairs.is_empty() {
        return Ok(Vec::new());
    }
    let mut by: HashMap<[u8; 16], Vec<(u64, String)>> = HashMap::new();
    for (n, k) in pairs {
        let m = crate::parse::load(n);
        by.entry(m.guid).or_default().push((*k, n.clone()));
    }
    let mut out = Vec::new();
    for (_g, mut rows) in by {
        rows.sort_by_key(|r| r.0);
        out.extend(rows.into_iter().map(|r| r.1));
    }
    Ok(out)
}
