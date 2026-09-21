use std::collections::BTreeMap;

pub fn rib_c(pairs: &[(String, u64)], root: Option<&str>) -> Result<Vec<String>, i32> {
    if let Some(r) = root {
        if r != "/app/dropwell" && !r.starts_with("/app/dropwell/") {
            return Err(1);
        }
    }
    if pairs.is_empty() {
        return Ok(Vec::new());
    }
    let mut by: BTreeMap<[u8; 16], Vec<(u8, u64, String)>> = BTreeMap::new();
    for (n, k) in pairs {
        let m = crate::parse::load(n);
        by.entry(m.guid)
            .or_default()
            .push((m.companion, *k, n.clone()));
    }
    let mut groups: Vec<(u64, Vec<String>)> = Vec::new();
    for (_g, mut rows) in by {
        let pk = rows
            .iter()
            .filter(|r| r.0 == 0)
            .map(|r| r.1)
            .min()
            .unwrap_or_else(|| rows.iter().map(|r| r.1).min().unwrap_or(0));
        rows.sort_by(|a, b| a.0.cmp(&b.0).then(a.2.cmp(&b.2)));
        groups.push((pk, rows.into_iter().map(|r| r.2).collect()));
    }
    groups.sort_by_key(|g| g.0);
    let mut out = Vec::new();
    for (_k, names) in groups {
        out.extend(names);
    }
    Ok(out)
}
