use crate::glyph;

fn clean_name(raw: &str) -> Result<String, String> {
    let name = glyph::fold_ascii(raw.trim());
    if name.is_empty() {
        return Err("empty aim name".into());
    }
    Ok(name)
}

/// Turn a YAML aim value into a name list and a kind tag.
/// A bare string is one name; a sequence is many names.
pub fn split_raw(v: &serde_yaml::Value) -> Result<(Vec<String>, String), String> {
    match v {
        serde_yaml::Value::String(s) => {
            let parts = glyph::expand_scalar_token(s);
            if parts.len() != 1 {
                return Err("bare aim must resolve to one name".into());
            }
            Ok((parts, "scalar".to_string()))
        }
        serde_yaml::Value::Sequence(seq) => {
            if seq.is_empty() {
                return Err("aim sequence must not be empty".into());
            }
            let mut out = Vec::new();
            let mut seen = std::collections::BTreeSet::new();
            for (idx, item) in seq.iter().enumerate() {
                let s = item
                    .as_str()
                    .ok_or_else(|| format!("aim sequence entry {idx} must be a string"))?;
                let name = clean_name(s)?;
                if seen.insert(name.clone()) {
                    out.push(name);
                }
            }
            Ok((out, "sequence".to_string()))
        }
        _ => Err(format!("unsupported aim type {:?}", v)),
    }
}
