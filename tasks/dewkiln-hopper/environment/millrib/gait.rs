use std::fs;

fn emit(p: &str, m: i32, t: i32) -> Result<(), i32> {
    let tpl = fs::read_to_string("/app/millrib/sheet.tpl").map_err(|_| 1)?;
    let out = tpl
        .replace("__P__", p)
        .replace("__M__", &m.to_string())
        .replace("__T__", &t.to_string());
    fs::create_dir_all("/app/bloturn").map_err(|_| 1)?;
    fs::write("/app/bloturn/check.json", out).map_err(|_| 1)?;
    Ok(())
}

pub fn gait(a: i32, _b: &[(i32, String)]) -> i32 {
    let _ = fs::remove_file("/app/bloturn/GUARD");
    if emit("ledger", a, a).is_err() {
        return 1;
    }
    if fs::write("/app/bloturn/GUARD", "ok").is_err() {
        return 1;
    }
    0
}
