pub struct Row {
    pub tag: String,
    pub pos: u32,
    pub n: u32,
}

fn tok(line: &str) -> Vec<String> {
    line.split_whitespace().map(|s| s.to_string()).collect()
}

pub fn rib_b() -> Vec<Row> {
    let text = std::fs::read_to_string("/app/ribcards/LAYOUT.txt").unwrap_or_default();
    let mut out = Vec::new();
    for line in text.lines() {
        let raw = line.trim();
        if raw.is_empty() || raw.starts_with('#') {
            continue;
        }
        let parts = tok(raw);
        if parts.len() < 3 {
            continue;
        }
        let tag = parts[0].clone();
        let mut pos: u32 = match parts[1].parse() {
            Ok(v) => v,
            Err(_) => continue,
        };
        let n: u32 = match parts[2].parse() {
            Ok(v) => v,
            Err(_) => continue,
        };
        if n > 8 {
            pos = pos.saturating_add(8 - (pos % 8));
        }
        out.push(Row { tag, pos, n });
    }
    out
}
