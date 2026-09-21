use std::collections::{BTreeMap, BTreeSet};
use std::env;
use std::fs;
use std::process;

include!("halt.rs");

type Item = (usize, usize);

#[derive(Clone, Debug, PartialEq, Eq)]
enum Act {
    Shift(usize),
    Reduce(usize),
    Acc,
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        eprintln!("usage: tblbake RECIPE OUTDIR");
        process::exit(2);
    }
    let text = fs::read_to_string(&args[1]).expect("recipe");
    let out = args[2].trim_end_matches('/').to_string();
    let _ = fs::create_dir_all(&out);

    let mut prods: Vec<(String, Vec<String>)> = Vec::new();
    prods.push(("S'".to_string(), vec!["S".to_string()]));
    let mut body = String::new();
    for line in text.lines() {
        let t = line.trim();
        if t.is_empty() || t.starts_with('#') {
            continue;
        }
        body.push_str(t);
        body.push(' ');
    }
    for chunk in body.split(';') {
        let chunk = chunk.trim();
        if chunk.is_empty() {
            continue;
        }
        let Some((lhs, rhs)) = chunk.split_once(':') else {
            continue;
        };
        let lhs = lhs.trim().to_string();
        for alt in rhs.split('|') {
            let syms: Vec<String> = alt.split_whitespace().map(|s| s.to_string()).collect();
            prods.push((lhs.clone(), syms));
        }
    }

    let mut nts: BTreeSet<String> = BTreeSet::new();
    for (l, _) in &prods {
        nts.insert(l.clone());
    }
    let mut terms: BTreeSet<String> = BTreeSet::new();
    terms.insert("$".to_string());
    for (_, rhs) in &prods {
        for s in rhs {
            if !nts.contains(s) {
                terms.insert(s.clone());
            }
        }
    }

    let mut first: BTreeMap<String, BTreeSet<Option<String>>> = BTreeMap::new();
    for nt in &nts {
        first.insert(nt.clone(), BTreeSet::new());
    }
    for t in &terms {
        let mut s = BTreeSet::new();
        s.insert(Some(t.clone()));
        first.insert(t.clone(), s);
    }
    let mut changed = true;
    while changed {
        changed = false;
        for (lhs, rhs) in &prods {
            if rhs.is_empty() {
                if first.get_mut(lhs).unwrap().insert(None) {
                    changed = true;
                }
                continue;
            }
            let mut nullable = true;
            for sym in rhs {
                let fs = first.get(sym).cloned().unwrap_or_default();
                for x in &fs {
                    if x.is_some() && first.get_mut(lhs).unwrap().insert(x.clone()) {
                        changed = true;
                    }
                }
                if !fs.contains(&None) {
                    nullable = false;
                    break;
                }
            }
            if nullable && first.get_mut(lhs).unwrap().insert(None) {
                changed = true;
            }
        }
    }

    let mut follow: BTreeMap<String, BTreeSet<String>> = BTreeMap::new();
    for nt in &nts {
        follow.insert(nt.clone(), BTreeSet::new());
    }
    follow.get_mut("S'").unwrap().insert("$".to_string());
    changed = true;
    while changed {
        changed = false;
        for (lhs, rhs) in &prods {
            for i in 0..rhs.len() {
                let sym = &rhs[i];
                if !nts.contains(sym) {
                    continue;
                }
                let rest = &rhs[i + 1..];
                let mut acc: BTreeSet<String> = BTreeSet::new();
                let mut nullable;
                if rest.is_empty() {
                    nullable = true;
                } else {
                    nullable = true;
                    for r in rest {
                        let fs = first.get(r).cloned().unwrap_or_default();
                        for x in &fs {
                            if let Some(t) = x {
                                acc.insert(t.clone());
                            }
                        }
                        if terms.contains(r) || !fs.contains(&None) {
                            nullable = false;
                            break;
                        }
                    }
                }
                for t in acc {
                    if follow.get_mut(sym).unwrap().insert(t) {
                        changed = true;
                    }
                }
                if nullable {
                    let extras = follow.get(lhs).cloned().unwrap_or_default();
                    for t in extras {
                        if follow.get_mut(sym).unwrap().insert(t) {
                            changed = true;
                        }
                    }
                }
            }
        }
    }

    fn closure(I: &BTreeSet<Item>, prods: &[(String, Vec<String>)], nts: &BTreeSet<String>) -> BTreeSet<Item> {
        let mut s = I.clone();
        let mut ch = true;
        while ch {
            ch = false;
            let snap: Vec<Item> = s.iter().cloned().collect();
            for (pi, dot) in snap {
                let rhs = &prods[pi].1;
                if dot < rhs.len() {
                    let b = &rhs[dot];
                    if nts.contains(b) {
                        for (j, (lhs, _)) in prods.iter().enumerate() {
                            if lhs == b && s.insert((j, 0)) {
                                ch = true;
                            }
                        }
                    }
                }
            }
        }
        s
    }

    fn goto_set(
        I: &BTreeSet<Item>,
        x: &str,
        prods: &[(String, Vec<String>)],
        nts: &BTreeSet<String>,
    ) -> BTreeSet<Item> {
        let mut j: BTreeSet<Item> = BTreeSet::new();
        for &(pi, dot) in I {
            let rhs = &prods[pi].1;
            if dot < rhs.len() && rhs[dot] == x {
                j.insert((pi, dot + 1));
            }
        }
        if j.is_empty() {
            BTreeSet::new()
        } else {
            closure(&j, prods, nts)
        }
    }

    let start = closure(&{
        let mut s = BTreeSet::new();
        s.insert((0, 0));
        s
    }, &prods, &nts);
    let mut csets: Vec<BTreeSet<Item>> = vec![start];
    changed = true;
    while changed {
        changed = false;
        let mut add: Vec<BTreeSet<Item>> = Vec::new();
        for i in &csets {
            let mut names: Vec<String> = nts.iter().cloned().collect();
            names.extend(terms.iter().filter(|t| *t != "$").cloned());
            for x in names {
                let g = goto_set(i, &x, &prods, &nts);
                if !g.is_empty() && !csets.contains(&g) && !add.contains(&g) {
                    add.push(g);
                    changed = true;
                }
            }
        }
        csets.extend(add);
    }

    let mut action: Vec<BTreeMap<String, Act>> = vec![BTreeMap::new(); csets.len()];
    let mut gotot: Vec<BTreeMap<String, usize>> = vec![BTreeMap::new(); csets.len()];
    let mut quarrel: Vec<String> = Vec::new();

    for (idx, i) in csets.iter().enumerate() {
        let mut names: Vec<String> = nts.iter().cloned().collect();
        names.extend(terms.iter().cloned());
        for x in &names {
            if nts.contains(x) {
                let g = goto_set(i, x, &prods, &nts);
                if !g.is_empty() {
                    if let Some(n) = csets.iter().position(|s| s == &g) {
                        gotot[idx].insert(x.clone(), n);
                    }
                }
            }
        }
        for &(pi, dot) in i {
            let lhs = &prods[pi].0;
            let rhs = &prods[pi].1;
            if dot < rhs.len() {
                let a = &rhs[dot];
                if terms.contains(a) {
                    let g = goto_set(i, a, &prods, &nts);
                    if let Some(n) = csets.iter().position(|s| s == &g) {
                        let neu = Act::Shift(n);
                        if let Some(old) = action[idx].get(a) {
                            if old != &neu {
                                quarrel.push(format!("state {} tok {}", idx, a));
                                if matches!(neu, Act::Shift(_)) {
                                    action[idx].insert(a.clone(), neu);
                                }
                            }
                        } else {
                            action[idx].insert(a.clone(), neu);
                        }
                    }
                }
            } else if lhs == "S'" {
                action[idx].insert("$".to_string(), Act::Acc);
            } else {
                for a in follow.get(lhs).cloned().unwrap_or_default() {
                    let neu = Act::Reduce(pi);
                    if let Some(old) = action[idx].get(&a) {
                        if old != &neu {
                            quarrel.push(format!("state {} tok {}", idx, a));
                            if matches!(old, Act::Reduce(_)) && matches!(neu, Act::Shift(_)) {
                                action[idx].insert(a.clone(), neu);
                            }
                        }
                    } else {
                        action[idx].insert(a.clone(), neu);
                    }
                }
            }
        }
    }

    let mut alines = String::new();
    for (si, row) in action.iter().enumerate() {
        for (t, act) in row {
            match act {
                Act::Shift(n) => alines.push_str(&format!("{} {} s {}\n", si, t, n)),
                Act::Reduce(p) => alines.push_str(&format!("{} {} r {}\n", si, t, p)),
                Act::Acc => alines.push_str(&format!("{} {} a 0\n", si, t)),
            }
        }
    }
    let mut glines = String::new();
    for (si, row) in gotot.iter().enumerate() {
        for (nt, n) in row {
            glines.push_str(&format!("{} {} {}\n", si, nt, n));
        }
    }
    let mut plines = String::new();
    for (i, (lhs, rhs)) in prods.iter().enumerate() {
        plines.push_str(&format!("{} {} {}\n", i, lhs, rhs.len()));
        for s in rhs {
            plines.push_str(&format!(" {}\n", s));
        }
    }
    fs::write(format!("{}/quarrel.lst", out), quarrel.join("\n")).unwrap();
    if rib_a(quarrel.len()) != 0 {
        process::exit(1);
    }
    fs::write(format!("{}/action.tbl", out), alines).unwrap();
    fs::write(format!("{}/goto.tbl", out), glines).unwrap();
    fs::write(format!("{}/prod.tbl", out), plines).unwrap();
    process::exit(0);
}
