use std::collections::BTreeMap;

pub fn pairs(blob: &[u8]) -> BTreeMap<String, String> {
    let mut m = BTreeMap::new();
    for line in String::from_utf8_lossy(blob).lines() {
        if let Some((k, v)) = line.split_once('=') {
            m.insert(k.trim().to_string(), v.trim().to_string());
        }
    }
    m
}
