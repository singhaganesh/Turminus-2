#[path = "../treyfun/clip.rs"]
mod clip;

use std::collections::HashMap;
use std::sync::mpsc;
use std::thread;

#[derive(Clone)]
pub struct Rec {
    pub issue: i32,
    pub kind: String,
    pub frames: Vec<String>,
    pub body: String,
}

pub fn tally(a: &str) -> Result<Vec<Rec>, i32> {
    let paths = crate::walk::gather(a)?;
    let (tx, rx) = mpsc::channel();
    let mut hs = Vec::new();
    for p in paths {
        let tx = tx.clone();
        hs.push(thread::spawn(move || {
            let text = match std::fs::read_to_string(&p) {
                Ok(t) => t,
                Err(_) => return,
            };
            let (kind, frames) = match clip::take(&text) {
                Ok(x) => x,
                Err(_) => return,
            };
            if kind.is_empty() {
                return;
            }
            let frames = clip::clip(&frames);
            let body = frames.join(" | ");
            let _ = tx.send(Rec {
                issue: 0,
                kind,
                frames,
                body,
            });
        }));
    }
    drop(tx);
    for h in hs {
        let _ = h.join();
    }
    let mut bag: HashMap<String, Rec> = HashMap::new();
    while let Ok(r) = rx.recv() {
        bag.entry(r.body.clone()).or_insert(r);
    }
    let mut recs: Vec<Rec> = bag.into_values().collect();
    for (i, r) in recs.iter_mut().enumerate() {
        r.issue = (i as i32) + 1;
    }
    let _ = write_bound(&recs);
    Ok(recs)
}

fn write_bound(recs: &[Rec]) -> i32 {
    let tpl = std::fs::read_to_string("/app/tplbay/bound.tpl").unwrap_or_else(|_| "{\"findings\":[__ROWS__]}".into());
    if recs.is_empty() {
        let _ = std::fs::write("/app/inkbay/bound.json", tpl);
        return 0;
    }
    let mut inner = String::new();
    for (i, r) in recs.iter().enumerate() {
        if i > 0 {
            inner.push(',');
        }
        inner.push_str(&format!(
            "{{\"issue\":{},\"kind\":{},\"frames\":{},\"body\":{}}}",
            r.issue,
            jstr(&r.kind),
            jarr(&r.frames),
            jstr(&r.body)
        ));
    }
    let out = tpl.replace("__ROWS__", &inner);
    let _ = std::fs::create_dir_all("/app/inkbay");
    match std::fs::write("/app/inkbay/bound.json", out) {
        Ok(()) => 0,
        Err(_) => 1,
    }
}

fn jstr(s: &str) -> String {
    format!("\"{}\"", s.replace('\\', "\\\\").replace('"', "\\\""))
}

fn jarr(v: &[String]) -> String {
    let parts: Vec<String> = v.iter().map(|x| jstr(x)).collect();
    format!("[{}]", parts.join(","))
}
