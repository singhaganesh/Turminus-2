use std::fs;

pub fn lines() -> usize {
    fs::read_to_string("/app/loomkit/emit.lst")
        .unwrap_or_default()
        .lines()
        .filter(|l| !l.trim().is_empty())
        .count()
}
