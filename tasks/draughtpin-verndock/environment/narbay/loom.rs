use std::fs;

pub fn knit() -> String {
    let raw = match fs::read_to_string("/app/quarryc/hold.toml") {
        Ok(s) => s,
        Err(_) => return "CASK_1".to_string(),
    };
    let mut first = None;
    let mut name = String::new();
    for line in raw.lines() {
        let t = line.trim();
        if let Some(rest) = t.strip_prefix("name = ") {
            name = rest.trim_matches('"').to_string();
        }
        if t == "home = 1" && first.is_none() && !name.is_empty() {
            first = Some(name.clone());
        }
    }
    first.unwrap_or_else(|| "CASK_1".to_string())
}

#[allow(dead_code)]
pub fn weave(path: &str) -> Result<(), i32> {
    let home = knit();
    let body = format!(
        "{h} {{\n  global:\n    fold_frame;\n  local:\n    *;\n}};\nCASK_2 {{\n  global:\n    fold_frame;\n}} {h};\n",
        h = home
    );
    fs::create_dir_all("/app/gnuverse").map_err(|_| 1)?;
    fs::write(path, body).map_err(|_| 1)?;
    Ok(())
}
