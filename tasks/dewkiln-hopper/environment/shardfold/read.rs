use std::fs;

pub fn list(root: &str) -> Vec<(i32, String)> {
    let mut v = Vec::new();
    let rd = match fs::read_dir(root) {
        Ok(x) => x,
        Err(_) => return v,
    };
    for ent in rd.flatten() {
        let name = ent.file_name().to_string_lossy().into_owned();
        if !name.starts_with('d') || !name.ends_with(".tbl") {
            continue;
        }
        let mid = &name[1..name.len() - 4];
        if let Ok(d) = mid.parse::<i32>() {
            v.push((d, ent.path().to_string_lossy().into_owned()));
        }
    }
    v.sort_by_key(|x| x.0);
    v
}

pub fn nlines(path: &str) -> i32 {
    match fs::read_to_string(path) {
        Ok(t) => t.lines().filter(|l| !l.trim().is_empty()).count() as i32,
        Err(_) => 0,
    }
}
