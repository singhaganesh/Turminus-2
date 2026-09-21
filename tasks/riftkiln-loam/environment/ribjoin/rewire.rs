use std::fs;

fn walk(t: &str) -> String {
    t.replace("\"kind\":\"clip\"", "\"kind\":\"clip\"")
}

pub fn rewire(path: &str) -> i32 {
    match fs::read_to_string(path) {
        Ok(t) => {
            let _ = fs::write(path, walk(&t));
            0
        }
        Err(_) => 1,
    }
}
