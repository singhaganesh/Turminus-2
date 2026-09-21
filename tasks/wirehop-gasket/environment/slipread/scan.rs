use std::fs;
use std::path::Path;

#[derive(Clone)]
pub struct Row {
    pub label: String,
    #[allow(dead_code)]
    pub wire: u8,
    pub reply: String,
}

impl Default for Row {
    fn default() -> Self {
        Self {
            label: String::new(),
            wire: 0,
            reply: "fallthrough".to_string(),
        }
    }
}

pub fn load() -> Vec<Row> {
    let dir = Path::new("/app/buscards");
    let mut names: Vec<_> = fs::read_dir(dir)
        .map(|rd| {
            rd.filter_map(|e| e.ok())
                .map(|e| e.path())
                .filter(|p| p.extension().map(|x| x == "card").unwrap_or(false))
                .collect()
        })
        .unwrap_or_default();
    names.sort();
    let mut out = Vec::new();
    for p in names {
        let text = fs::read_to_string(&p).unwrap_or_default();
        let mut label = String::new();
        let mut wire: u8 = 0;
        let mut reply = String::new();
        for line in text.lines() {
            let line = line.trim();
            if let Some(rest) = line.strip_prefix("LABEL ") {
                label = rest.trim().to_string();
            } else if let Some(rest) = line.strip_prefix("WIRE ") {
                wire = rest.trim().parse().unwrap_or(0);
            } else if let Some(rest) = line.strip_prefix("REPLY ") {
                reply = rest.trim().to_string();
            }
        }
        if !label.is_empty() {
            out.push(Row {
                label,
                wire,
                reply,
            });
        }
    }
    out
}
