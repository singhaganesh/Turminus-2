use std::fs;

pub fn floor(a: i32) -> bool {
    let t = match fs::read_to_string("/app/floorcue/MIN.txt") {
        Ok(s) => s.trim().parse::<i32>().unwrap_or(0),
        Err(_) => 0,
    };
    a >= t
}
