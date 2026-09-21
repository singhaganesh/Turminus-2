use std::fs;

pub fn soak(a: &[(i32, String)], b: &str) -> Result<(), i32> {
    let _ = fs::remove_dir_all(b);
    fs::create_dir_all(b).map_err(|_| 1)?;
    let mut xs: Vec<(i32, String)> = a.to_vec();
    xs.sort_by_key(|x| x.0);
    for (d, p) in xs {
        let name = format!("d{:08}.tbl", d);
        fs::copy(&p, format!("{}/{}", b, name)).map_err(|_| 1)?;
    }
    Ok(())
}
