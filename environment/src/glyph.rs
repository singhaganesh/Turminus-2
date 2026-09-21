/// Fold trivial ASCII whitespace noise. Does not rewrite punctuation.
pub fn fold_ascii(raw: &str) -> String {
    raw.chars()
        .map(|c| if c == '\u{00a0}' { ' ' } else { c })
        .collect::<String>()
        .trim()
        .to_string()
}

/// Expand a bare aim token into planner name units.
pub fn expand_scalar_token(raw: &str) -> Vec<String> {
    let folded = fold_ascii(raw);
    if folded.is_empty() {
        return Vec::new();
    }
    if folded.chars().any(|c| c.is_whitespace()) {
        return folded
            .split_whitespace()
            .map(|part| fold_ascii(part))
            .filter(|part| !part.is_empty())
            .collect();
    }
    vec![folded]
}
