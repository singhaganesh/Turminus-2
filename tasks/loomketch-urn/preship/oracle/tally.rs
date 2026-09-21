#[path = "../treyfun/clip.rs"]
mod clip;

use std::collections::BTreeMap;

#[derive(Clone)]
pub struct Rec {
    pub issue: i32,
    pub kind: String,
    pub frames: Vec<String>,
    pub body: String,
}

pub fn tally(a: &str) -> Result<Vec<Rec>, i32> {
    if !a.starts_with("/app/vatlogs") {
        return Err(3);
    }
    let paths = crate::walk::gather(a)?;
    let mut bag: BTreeMap<String, Rec> = BTreeMap::new();
    for p in paths {
        let text = match std::fs::read_to_string(&p) {
            Ok(t) => t,
            Err(_) => return Err(2),
        };
        let (kind, raw) = clip::take(&text)?;
        let frames = clip::clip(&raw);
        if frames.is_empty() {
            return Err(2);
        }
        let body = frames.join(" | ");
        bag.entry(body.clone()).or_insert(Rec {
            issue: 0,
            kind,
            frames,
            body,
        });
    }
    let mut recs: Vec<Rec> = bag.into_values().collect();
    recs.sort_by(|x, y| x.body.cmp(&y.body).then(x.kind.cmp(&y.kind)));
    for (i, r) in recs.iter_mut().enumerate() {
        r.issue = (i as i32) + 1;
    }
    write_bound(&recs)?;
    Ok(recs)
}

fn write_bound(recs: &[Rec]) -> Result<(), i32> {
    let tpl = std::fs::read_to_string("/app/tplbay/bound.tpl").map_err(|_| 1)?;
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
    std::fs::create_dir_all("/app/inkbay").map_err(|_| 1)?;
    std::fs::write("/app/inkbay/bound.json", out).map_err(|_| 1)?;
    Ok(())
}

fn jstr(s: &str) -> String {
    format!("\"{}\"", s.replace('\\', "\\\\").replace('"', "\\\""))
}

fn jarr(v: &[String]) -> String {
    let parts: Vec<String> = v.iter().map(|x| jstr(x)).collect();
    format!("[{}]", parts.join(","))
}
