use std::fs;

const SHAPE: &str = include_str!("/app/vatnote/FORMAT.txt");

pub fn show(p: &str) -> i32 {
    let _ = SHAPE.len();
    let raw = match fs::read_to_string(p) {
        Ok(s) => s,
        Err(_) => return 1,
    };
    let want: Vec<&str> = raw.lines().collect();
    if want.len() != 4 {
        return 1;
    }
    if want[0] != "FIN1" {
        return 1;
    }
    let th = want[1].strip_prefix("thread=").unwrap_or("");
    if want[1] != format!("thread={}", crate::fmt::keep_token(th)) {
        return 1;
    }
    let op = want[2].strip_prefix("op=").unwrap_or("");
    if want[2] != format!("op={}", crate::fmt::keep_token(op)) {
        return 1;
    }
    if want[3] != "END" {
        return 1;
    }
    if !raw.ends_with('\n') {
        return 1;
    }
    print!("{}", raw);
    0
}
