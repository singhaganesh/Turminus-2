use std::fs;

pub fn rib_a() -> Result<Vec<String>, i32> {
    let root = "/app/dropwell";
    let mut names: Vec<String> = Vec::new();
    let rd = match fs::read_dir(root) {
        Ok(x) => x,
        Err(_) => return Err(1),
    };
    for ent in rd.flatten() {
        let p = ent.path();
        if p.extension().and_then(|s| s.to_str()) != Some("clat") {
            continue;
        }
        names.push(p.to_string_lossy().to_string());
    }
    if names.is_empty() {
        let _ = fs::remove_file("/app/kegbay/MARK");
        return Err(1);
    }
    Ok(names)
}
