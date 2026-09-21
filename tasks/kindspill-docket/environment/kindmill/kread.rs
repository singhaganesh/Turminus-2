use std::fs;
use std::path::{Path, PathBuf};

pub struct Sheet {
    pub raw: String,
    pub rank: u8,
}

#[allow(dead_code)]
pub fn fold(s: &str) -> String {
    s.trim().to_ascii_lowercase().replace('-', "_")
}

pub fn desc_dir() -> PathBuf {
    PathBuf::from("/app/sanitdesc")
}

pub fn load_glob() -> Vec<Sheet> {
    let mut paths: Vec<PathBuf> = match fs::read_dir(desc_dir()) {
        Ok(rd) => rd.filter_map(|e| e.ok()).map(|e| e.path()).collect(),
        Err(_) => Vec::new(),
    };
    paths.retain(|p| p.extension().and_then(|s| s.to_str()) == Some("kind"));
    paths.sort();
    paths.into_iter().map(|p| parse_sheet(&p)).collect()
}

fn parse_sheet(p: &Path) -> Sheet {
    let t = fs::read_to_string(p).unwrap_or_default();
    let mut raw = String::new();
    let mut rank = 0u8;
    for line in t.lines() {
        let line = line.trim();
        if let Some(rest) = line.strip_prefix("KIND") {
            raw = rest.trim().to_string();
        }
        if let Some(rest) = line.strip_prefix("RANK") {
            rank = rest.trim().parse().unwrap_or(0);
        }
    }
    Sheet { raw, rank }
}

pub fn put_rec(buf: &mut Vec<u8>, name: &str, rank: u8) {
    let b = name.as_bytes();
    let n = b.len() as u16;
    buf.extend_from_slice(&n.to_be_bytes());
    buf.extend_from_slice(b);
    buf.push(rank);
}

pub fn parse_recs(bytes: &[u8]) -> Vec<(String, u8)> {
    let mut out = Vec::new();
    let mut i = 0usize;
    while i + 3 <= bytes.len() {
        let n = u16::from_be_bytes([bytes[i], bytes[i + 1]]) as usize;
        i += 2;
        if i + n + 1 > bytes.len() {
            break;
        }
        let name = String::from_utf8_lossy(&bytes[i..i + n]).into_owned();
        i += n;
        let rank = bytes[i];
        i += 1;
        out.push((name, rank));
    }
    out
}
