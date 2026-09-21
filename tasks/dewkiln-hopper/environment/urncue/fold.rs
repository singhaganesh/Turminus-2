#[path = "../hopcue/rim.rs"]
mod rim;
#[path = "../restpit/soak.rs"]
mod soak;
#[path = "../shardfold/read.rs"]
mod read;

use std::fs;

pub fn fold() -> Result<(Vec<(i32, String)>, i32), i32> {
    let wall: i32 = fs::read_to_string("/app/opstext/WALL")
        .map_err(|_| 1)?
        .trim()
        .parse()
        .map_err(|_| 1)?;
    let listed = read::list("/app/daywell");
    let picked = rim::rim(wall, listed);
    if picked.is_empty() {
        fs::create_dir_all("/app/bloturn").map_err(|_| 1)?;
        fs::write("/app/bloturn/ledger.json", "{\"taken\":0}").map_err(|_| 1)?;
        let _ = fs::remove_dir_all("/app/packbay/stage");
        let _ = fs::remove_dir_all("/app/packbay/latest");
        fs::create_dir_all("/app/packbay/stage").ok();
        fs::create_dir_all("/app/packbay/latest").ok();
        return Ok((Vec::new(), 0));
    }
    let _ = fs::remove_dir_all("/app/packbay/stage");
    fs::create_dir_all("/app/packbay/stage").map_err(|_| 1)?;
    let mut packed = Vec::new();
    let mut taken = 0;
    for (d, p) in picked {
        let name = format!("d{:08}.tbl", d);
        let dest = format!("/app/packbay/stage/{}", name);
        fs::copy(&p, &dest).map_err(|_| 1)?;
        taken += read::nlines(&dest);
        packed.push((d, dest));
    }
    soak::soak(&packed, "/app/packbay/latest")?;
    fs::create_dir_all("/app/bloturn").map_err(|_| 1)?;
    let body = format!("{{\"taken\":{}}}", taken);
    fs::write("/app/bloturn/ledger.json", body).map_err(|_| 1)?;
    Ok((packed, taken))
}
