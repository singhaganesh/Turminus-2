use std::process::Command;

pub fn hex_file(path: &str) -> String {
    let out = Command::new("sha256sum")
        .arg(path)
        .output()
        .ok()
        .and_then(|o| String::from_utf8(o.stdout).ok())
        .unwrap_or_default();
    out.split_whitespace().next().unwrap_or("").to_string()
}
