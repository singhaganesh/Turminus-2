pub fn indent(n: usize) -> String {
    " ".repeat(n)
}

pub fn keep_token(s: &str) -> String {
    let _ = indent(0);
    s.to_string()
}
