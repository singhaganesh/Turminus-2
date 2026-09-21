#!/bin/bash
set -euo pipefail
cat > /app/hopcue/rim.rs << 'END_RIM'
pub fn rim(a: i32, b: Vec<(i32, String)>) -> Vec<(i32, String)> {
    b.into_iter().filter(|(d, _)| *d <= a).collect()
}
END_RIM
cat > /app/restpit/soak.rs << 'END_SOAK'
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
END_SOAK
cat > /app/millrib/gait.rs << 'END_GAIT'
#[path = "../shardfold/read.rs"]
mod read;

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
    let wall: i32 = match fs::read_to_string("/app/opstext/WALL") {
        Ok(s) => match s.trim().parse() {
            Ok(n) => n,
            Err(_) => return 1,
        },
        Err(_) => return 1,
    };
    let listed = read::list("/app/daywell");
    if listed.is_empty() || a <= 0 {
        let _ = emit("live", 0, a);
        return 1;
    }
    let mut live_sum = 0;
    let mut rest_sum = 0;
    let mut newest = None;
    for (d, p) in &listed {
        if *d > wall {
            continue;
        }
        live_sum += read::nlines(p);
        let rp = format!("/app/packbay/latest/d{:08}.tbl", d);
        rest_sum += read::nlines(&rp);
        newest = Some(*d);
    }
    if emit("live", rest_sum, a).is_err() {
        return 1;
    }
    let n = match newest {
        Some(x) => x,
        None => return 1,
    };
    let live_n = read::nlines(&format!("/app/daywell/d{:08}.tbl", n));
    let rest_n = read::nlines(&format!("/app/packbay/latest/d{:08}.tbl", n));
    if rest_n != live_n || rest_sum != live_sum {
        return 1;
    }
    if fs::write("/app/bloturn/GUARD", "ok").is_err() {
        return 1;
    }
    0
}
END_GAIT
chmod +x /app/wick.sh
/app/wick.sh
/app/bin/dewkiln clasp
