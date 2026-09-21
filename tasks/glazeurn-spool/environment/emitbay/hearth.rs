use std::fs;

pub fn rib_d() -> i32 {
    let _ = fs::read_dir("/app/daycards");
    let rim = r#"use crate::hold;

pub fn rim_a(a: &hold::Sess, b: &hold::Pool) -> hold::Frost {
    let _ = b;
    hold::Frost {
        n0: a.n0,
        n1: a.n1,
        ids: a.ids.clone(),
        cells: Vec::new(),
    }
}
"#;
    let pool = r#"use crate::fold;
use crate::hold;
use crate::load;
use crate::tally;
use std::fs;
use std::path::Path;

pub fn rim_b(a: &mut hold::Frost, b: &hold::Pool) {
    let _ = (a, b);
}

pub fn prep(a: &hold::Sess, b: &hold::Pool) -> hold::Frost {
    let mut f = fold::rim_a(a, b);
    rim_b(&mut f, b);
    f
}

fn pack(ids: &[usize], cells: &[String]) -> String {
    let mut parts = Vec::new();
    for &i in ids {
        let s = cells.get(i).map(|x| x.as_str()).unwrap_or("");
        parts.push(format!("\"{}\"", s));
    }
    format!("[{}]", parts.join(","))
}

pub fn dump() -> i32 {
    let Some((mut sess, mut pool, plan)) = load::read_path("/app/spoolbay/shift.spool") else {
        return 1;
    };
    let frost = prep(&sess, &pool);
    load::step(&mut sess, &mut pool, &plan);
    let live_ids = sess.ids.borrow().clone();
    let frost_ids = frost.ids.borrow().clone();
    let extra = tally::lines();
    let frost_s = pack(&frost_ids, &frost.cells);
    let live_s = pack(&live_ids, &pool.cells);
    let dest = Path::new("/app/inkpit/pair.json");
    if let Some(parent) = dest.parent() {
        let _ = fs::create_dir_all(parent);
    }
    let body = format!(
        "{{\"tick\":{},\"mark\":{},\"frost_bag\":{},\"live_bag\":{}}}\n",
        sess.n0.saturating_add(extra),
        sess.n1,
        frost_s,
        live_s
    );
    match fs::write(dest, body) {
        Ok(()) => 0,
        Err(_) => 2,
    }
}
"#;
    let ink = r#"use crate::load;
use crate::pool;
use crate::tally;
use std::fs;
use std::path::Path;

pub fn rim_c() -> i32 {
    let _ = tally::lines();
    let dest = Path::new("/app/inkpit/pair.json");
    let guard = Path::new("/app/inkpit/GUARD");
    if let Some(parent) = dest.parent() {
        let _ = fs::create_dir_all(parent);
    }
    if load::read_path("/app/spoolbay/shift.spool").is_none() {
        let _ = fs::write(
            dest,
            "{\"tick\":0,\"mark\":0,\"frost_bag\":[],\"live_bag\":[]}\n",
        );
        let _ = fs::write(guard, "ok\n");
        return 0;
    }
    let _ = pool::dump();
    let _ = fs::write(guard, "ok\n");
    0
}
"#;
    if fs::write("/app/foldrib/rim.rs", rim).is_err() {
        return 2;
    }
    if fs::write("/app/internpit/pool.rs", pool).is_err() {
        return 2;
    }
    if fs::write("/app/restcue/ink.rs", ink).is_err() {
        return 2;
    }
    0
}
