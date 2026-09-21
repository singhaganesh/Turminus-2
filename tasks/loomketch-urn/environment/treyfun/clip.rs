pub fn clip(a: &[String]) -> Vec<String> {
    a.iter()
        .filter(|s| !s.starts_with("__asan::") && !s.starts_with("__asan_"))
        .cloned()
        .collect()
}

pub fn take(text: &str) -> Result<(String, Vec<String>), i32> {
    if text.trim().is_empty() {
        return Ok((String::new(), Vec::new()));
    }
    let mut kind = String::new();
    let mut frames = Vec::new();
    for line in text.lines() {
        if let Some(rest) = line.split("ERROR:").nth(1) {
            let rest = rest.trim();
            let after = if let Some(x) = rest.split("AddressSanitizer:").nth(1) {
                x.trim()
            } else {
                rest
            };
            kind = after.split(" on ").next().unwrap_or(after).trim().to_string();
        }
        if let Some(idx) = line.find('#') {
            let chunk = &line[idx..];
            if let Some(after) = chunk.split(" in ").nth(1) {
                let sym = after.split_whitespace().next().unwrap_or("").to_string();
                if !sym.is_empty() {
                    frames.push(sym);
                }
            }
        }
    }
    Ok((kind, frames))
}
