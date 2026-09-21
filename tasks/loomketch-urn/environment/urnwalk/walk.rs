pub fn gather(a: &str) -> Result<Vec<String>, i32> {
    let mut v = Vec::new();
    let rd = match std::fs::read_dir(a) {
        Ok(x) => x,
        Err(_) => return Err(2),
    };
    for e in rd {
        let e = match e {
            Ok(x) => x,
            Err(_) => continue,
        };
        let p = e.path();
        if p.is_file() {
            v.push(p.to_string_lossy().into_owned());
        }
    }
    if crate::alpha::lined(&mut v) {
        v.sort();
    }
    Ok(v)
}
