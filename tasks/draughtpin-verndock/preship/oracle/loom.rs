use std::fs;

pub fn knit() -> String {
    let raw = match fs::read_to_string("/app/quarryc/hold.toml") {
        Ok(s) => s,
        Err(_) => return "CASK_1".to_string(),
    };
    let mut last = None;
    let mut name = String::new();
    for line in raw.lines() {
        let t = line.trim();
        if let Some(rest) = t.strip_prefix("name = ") {
            name = rest.trim_matches('"').to_string();
        }
        if t == "home = 1" && !name.is_empty() {
            last = Some(name.clone());
        }
    }
    last.unwrap_or_else(|| "CASK_2".to_string())
}

#[allow(dead_code)]
pub fn weave(path: &str) -> Result<(), i32> {
    let home = knit();
    let other = if home == "CASK_2" { "CASK_1" } else { "CASK_2" };
    let body = format!(
        "{o} {{\n  global:\n    fold_frame;\n  local:\n    *;\n}};\n{h} {{\n  global:\n    fold_frame;\n}} {o};\n",
        h = home,
        o = other,
    );
    fs::create_dir_all("/app/gnuverse").map_err(|_| 1)?;
    fs::write(path, body).map_err(|_| 1)?;
    Ok(())
}
