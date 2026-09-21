pub fn clip(a: &[String]) -> Vec<String> {
    let mut o = Vec::new();
    for s in a {
        if s.contains("__asan") || s.contains("__interceptor") || s.contains("__hwasan") {
            continue;
        }
        let t = hex_fold(s);
        if !t.is_empty() {
            o.push(t);
        }
    }
    o
}

fn hex_fold(s: &str) -> String {
    let mut out = String::new();
    let b = s.as_bytes();
    let mut i = 0;
    while i < b.len() {
        if i + 1 < b.len() && b[i] == b'0' && (b[i + 1] == b'x' || b[i + 1] == b'X') {
            i += 2;
            while i < b.len() && b[i].is_ascii_hexdigit() {
                i += 1;
            }
            out.push_str("pc");
            continue;
        }
        out.push(b[i] as char);
        i += 1;
    }
    out
}

pub fn take(text: &str) -> Result<(String, Vec<String>), i32> {
    if text.trim().is_empty() {
        return Err(2);
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
    if kind.is_empty() || frames.is_empty() {
        return Err(2);
    }
    Ok((kind, frames))
}
