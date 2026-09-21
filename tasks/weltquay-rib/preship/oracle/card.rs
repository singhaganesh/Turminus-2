pub struct Row {
    pub tag: String,
    pub pos: u32,
    pub n: u32,
}

fn parse_u32(raw: &str) -> Option<u32> {
    raw.parse().ok()
}

pub fn rib_b() -> Vec<Row> {
    let text = std::fs::read_to_string("/app/ribcards/LAYOUT.txt").unwrap_or_default();
    let mut out = Vec::new();
    for line in text.lines() {
        let raw = line.trim();
        if raw.is_empty() || raw.starts_with('#') {
            continue;
        }
        let mut it = raw.split_whitespace();
        let tag = match it.next() {
            Some(v) => v.to_string(),
            None => continue,
        };
        let pos = match it.next().and_then(parse_u32) {
            Some(v) => v,
            None => continue,
        };
        let n = match it.next().and_then(parse_u32) {
            Some(v) => v,
            None => continue,
        };
        out.push(Row { tag, pos, n });
    }
    out
}
