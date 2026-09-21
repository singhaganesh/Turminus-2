use crate::hold;
use std::cell::RefCell;
use std::fs;
use std::rc::Rc;

pub struct Plan {
    pub old: String,
    pub new: String,
    pub extra: String,
}

pub fn kiln_pitch(n0: u32, n1: u32) -> (u32, u32) {
    (n0.saturating_add(1), n1.saturating_add(2))
}

pub fn read_path(p: &str) -> Option<(hold::Sess, hold::Pool, Plan)> {
    let text = fs::read_to_string(p).ok()?;
    if text.trim().is_empty() {
        return None;
    }
    let mut n0 = None;
    let mut n1 = None;
    let mut cells: Vec<String> = Vec::new();
    let mut flag = false;
    let mut old = String::new();
    let mut new = String::new();
    let mut extra = String::new();
    for raw in text.lines() {
        let line = raw.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        let mut it = line.split_whitespace();
        let key = it.next()?;
        match key {
            "tick" => n0 = it.next()?.parse().ok(),
            "mark" => n1 = it.next()?.parse().ok(),
            "bag" => cells = it.map(|s| s.to_string()).collect(),
            "mode" => flag = it.next() == Some("heat"),
            "swap" => {
                old = it.next()?.to_string();
                new = it.next()?.to_string();
            }
            "push" => extra = it.next()?.to_string(),
            _ => {}
        }
    }
    let n0 = n0?;
    let n1 = n1?;
    if cells.is_empty() {
        return None;
    }
    let ids: Vec<usize> = (0..cells.len()).collect();
    let sess = hold::Sess {
        n0,
        n1,
        ids: Rc::new(RefCell::new(ids)),
        flag,
    };
    let pool = hold::Pool { cells };
    Some((sess, pool, Plan { old, new, extra }))
}

pub fn step(a: &mut hold::Sess, b: &mut hold::Pool, p: &Plan) {
    if a.flag {
        for c in b.cells.iter_mut() {
            if *c == p.old {
                *c = p.new.clone();
            }
        }
        if !p.extra.is_empty() {
            b.cells.push(p.extra.clone());
            a.ids.borrow_mut().push(b.cells.len() - 1);
        }
    }
    let (tick, mark) = kiln_pitch(a.n0, a.n1);
    a.n0 = tick;
    a.n1 = mark;
}
