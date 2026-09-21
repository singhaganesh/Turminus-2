use crate::fold;
use crate::hold;
use crate::load;
use crate::tally;
use std::fs;
use std::path::Path;

pub fn rim_b(a: &mut hold::Frost, b: &hold::Pool) {
    a.cells = b.cells.clone();
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
        Ok(()) => {
            if sess.flag && frost_s == live_s {
                1
            } else {
                0
            }
        }
        Err(_) => 2,
    }
}
