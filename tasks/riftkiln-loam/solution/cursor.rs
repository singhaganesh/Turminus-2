use std::collections::BTreeMap;
use std::fs;

#[derive(Clone, Debug)]
enum Node {
    Str(String),
    List(Vec<Node>),
    Map(Vec<(String, Node)>),
}

fn map_get<'a>(n: &'a Node, k: &str) -> Option<&'a Node> {
    if let Node::Map(pairs) = n {
        for (a, b) in pairs {
            if a == k {
                return Some(b);
            }
        }
    }
    None
}

fn map_get_mut<'a>(n: &'a mut Node, k: &str) -> Option<&'a mut Node> {
    if let Node::Map(pairs) = n {
        for (a, b) in pairs.iter_mut() {
            if a == k {
                return Some(b);
            }
        }
    }
    None
}

fn kind_of(n: &Node) -> String {
    match map_get(n, "kind") {
        Some(Node::Str(s)) => s.clone(),
        _ => String::new(),
    }
}

pub fn rib_c(mut acc: Node, neu: Node) -> Node {
    if let Node::List(ref mut items) = acc {
        append_kid(items, neu);
        return acc;
    }
    acc
}

fn append_kid(items: &mut Vec<Node>, neu: Node) {
    items.push(neu);
}

fn stem_of(n: &Node) -> String {
    match map_get(n, "stem") {
        Some(Node::Str(s)) => s.clone(),
        _ => String::new(),
    }
}

fn tag_of(n: &Node) -> String {
    match map_get(n, "tag") {
        Some(Node::Str(s)) => s.clone(),
        _ => String::new(),
    }
}

fn mark_of(n: &Node) -> String {
    match map_get(n, "mark") {
        Some(Node::Str(s)) => s.clone(),
        _ => String::new(),
    }
}

fn str_kid(kids: &[Node], i: usize) -> String {
    if i >= kids.len() {
        return String::new();
    }
    match &kids[i] {
        Node::Str(s) => s.clone(),
        _ => String::new(),
    }
}

fn to_json(n: &Node) -> String {
    match n {
        Node::Str(s) => format!("\"{}\"", s.replace('\\', "\\\\").replace('"', "\\\"")),
        Node::List(xs) => {
            let inner: Vec<String> = xs.iter().map(to_json).collect();
            format!("[{}]", inner.join(","))
        }
        Node::Map(pairs) => {
            let inner: Vec<String> = pairs
                .iter()
                .map(|(k, v)| format!("\"{}\":{}", k, to_json(v)))
                .collect();
            format!("{{{}}}", inner.join(","))
        }
    }
}

#[derive(Clone)]
enum Cell {
    S(usize),
    R(usize),
    A,
}

fn load_action(path: &str) -> BTreeMap<(usize, String), Cell> {
    let mut m = BTreeMap::new();
    if let Ok(t) = fs::read_to_string(path) {
        for line in t.lines() {
            let p: Vec<&str> = line.split_whitespace().collect();
            if p.len() < 4 {
                continue;
            }
            let st: usize = p[0].parse().unwrap_or(0);
            let tok = p[1].to_string();
            m.insert(
                (st, tok),
                match p[2] {
                    "s" => Cell::S(p[3].parse().unwrap_or(0)),
                    "r" => Cell::R(p[3].parse().unwrap_or(0)),
                    _ => Cell::A,
                },
            );
        }
    }
    m
}

fn load_goto(path: &str) -> BTreeMap<(usize, String), usize> {
    let mut m = BTreeMap::new();
    if let Ok(t) = fs::read_to_string(path) {
        for line in t.lines() {
            let p: Vec<&str> = line.split_whitespace().collect();
            if p.len() < 3 {
                continue;
            }
            m.insert(
                (p[0].parse().unwrap_or(0), p[1].to_string()),
                p[2].parse().unwrap_or(0),
            );
        }
    }
    m
}

fn load_prod(path: &str) -> Vec<(String, Vec<String>)> {
    let mut out = Vec::new();
    let t = fs::read_to_string(path).unwrap_or_default();
    let lines: Vec<&str> = t.lines().collect();
    let mut i = 0;
    while i < lines.len() {
        let p: Vec<&str> = lines[i].split_whitespace().collect();
        if p.len() >= 3 {
            let n: usize = p[2].parse().unwrap_or(0);
            let mut rhs = Vec::new();
            for _ in 0..n {
                i += 1;
                if i < lines.len() {
                    rhs.push(lines[i].trim().to_string());
                }
            }
            let idx: usize = p[0].parse().unwrap_or(0);
            while out.len() <= idx {
                out.push((String::new(), Vec::new()));
            }
            out[idx] = (p[1].to_string(), rhs);
        }
        i += 1;
    }
    out
}

#[derive(Clone)]
struct Tok {
    name: String,
    lex: String,
}

fn lex(src: &str) -> Vec<Tok> {
    let mut out = Vec::new();
    let b = src.as_bytes();
    let mut i = 0;
    let mut after_eq = false;
    while i < b.len() {
        let c = b[i] as char;
        if c.is_whitespace() {
            i += 1;
            continue;
        }
        if c == '{' {
            out.push(Tok {
                name: "LBRACE".into(),
                lex: "{".into(),
            });
            i += 1;
            continue;
        }
        if c == '}' {
            out.push(Tok {
                name: "RBRACE".into(),
                lex: "}".into(),
            });
            i += 1;
            continue;
        }
        if c == '=' {
            out.push(Tok {
                name: "EQ".into(),
                lex: "=".into(),
            });
            after_eq = true;
            i += 1;
            continue;
        }
        if c == ';' {
            out.push(Tok {
                name: "SEMI".into(),
                lex: ";".into(),
            });
            i += 1;
            continue;
        }
        if c.is_ascii_alphanumeric() || c == '_' {
            let s = i;
            i += 1;
            while i < b.len() {
                let d = b[i] as char;
                if d.is_ascii_alphanumeric() || d == '_' {
                    i += 1;
                } else {
                    break;
                }
            }
            let w = src[s..i].to_string();
            if after_eq {
                out.push(Tok {
                    name: "VAL".into(),
                    lex: w,
                });
                after_eq = false;
            } else {
                let name = match w.as_str() {
                    "yard" => "YARD",
                    "pen" => "PEN",
                    "clip" => "CLIP",
                    "peg" => "PEG",
                    _ => "ID",
                };
                out.push(Tok {
                    name: name.into(),
                    lex: w,
                });
            }
            continue;
        }
        i += 1;
    }
    out.push(Tok {
        name: "$".into(),
        lex: "".into(),
    });
    out
}

fn reduce_node(prod: &(String, Vec<String>), kids: Vec<Node>) -> Node {
    let lhs = &prod.0;
    let rhs = &prod.1;
    if lhs == "MS" && rhs.is_empty() {
        return Node::List(Vec::new());
    }
    if lhs == "MS" && rhs.len() == 2 {
        return rib_c(kids[0].clone(), kids[1].clone());
    }
    if lhs == "M" && rhs.first().map(|s| s.as_str()) == Some("PEG") {
        let tag = if let Node::Str(s) = &kids[1] {
            s.clone()
        } else {
            String::new()
        };
        let mark = if let Node::Str(s) = &kids[3] {
            s.clone()
        } else {
            String::new()
        };
        return Node::Map(vec![
            ("kind".into(), Node::Str("peg".into())),
            ("tag".into(), Node::Str(tag)),
            ("mark".into(), Node::Str(mark)),
        ]);
    }
    if lhs == "M" && rhs.first().map(|s| s.as_str()) == Some("CLIP") && rhs.len() == 2 {
        let stem = if let Node::Str(s) = &kids[1] {
            s.clone()
        } else {
            String::new()
        };
        return Node::Map(vec![
            ("kind".into(), Node::Str("clip".into())),
            ("stem".into(), Node::Str(stem)),
        ]);
    }
    if lhs == "M" && rhs.first().map(|s| s.as_str()) == Some("PEN") {
        let stem = if let Node::Str(s) = &kids[1] {
            s.clone()
        } else {
            String::new()
        };
        let members = kids[3].clone();
        return Node::Map(vec![
            ("kind".into(), Node::Str("pen".into())),
            ("stem".into(), Node::Str(stem)),
            ("members".into(), members),
        ]);
    }
    if lhs == "S" {
        let yard = if let Node::Str(s) = &kids[1] {
            s.clone()
        } else {
            String::new()
        };
        let members = kids[3].clone();
        return Node::Map(vec![
            ("yard".into(), Node::Str(yard)),
            ("members".into(), members),
        ]);
    }
    if lhs == "S'" {
        return kids[0].clone();
    }
    Node::List(kids)
}

fn tbl_dir() -> String {
    std::env::var("ACTRIB").unwrap_or_else(|_| "/app/tblwell".to_string())
}

pub fn run_sift(src: &str, dest: &str) -> i32 {
    let text = match fs::read_to_string(src) {
        Ok(t) => t,
        Err(_) => return 1,
    };
    let toks = lex(&text);
    let base = tbl_dir();
    let act = load_action(&format!("{}/action.tbl", base));
    let gtbl = load_goto(&format!("{}/goto.tbl", base));
    let prods = load_prod(&format!("{}/prod.tbl", base));
    let mut states: Vec<usize> = vec![0];
    let mut vals: Vec<Node> = Vec::new();
    let mut ip = 0;
    loop {
        if ip >= toks.len() {
            return 1;
        }
        let st = *states.last().unwrap();
        let la = &toks[ip].name;
        let cell = act.get(&(st, la.clone()));
        match cell {
            Some(Cell::S(n)) => {
                vals.push(Node::Str(toks[ip].lex.clone()));
                states.push(*n);
                ip += 1;
            }
            Some(Cell::R(p)) => {
                if *p >= prods.len() {
                    return 1;
                }
                let prod = &prods[*p];
                let n = prod.1.len();
                if states.len() < n || vals.len() < n {
                    return 1;
                }
                let mut kids = Vec::new();
                for _ in 0..n {
                    states.pop();
                    kids.push(vals.pop().unwrap());
                }
                kids.reverse();
                let built = reduce_node(prod, kids);
                let st2 = *states.last().unwrap();
                match gtbl.get(&(st2, prod.0.clone())) {
                    Some(ns) => {
                        vals.push(built);
                        states.push(*ns);
                    }
                    None => {
                        if prod.0 == "S'" {
                            let _ = fs::write(dest, to_json(&built));
                            return 0;
                        }
                        return 1;
                    }
                }
            }
            Some(Cell::A) => {
                if let Some(built) = vals.last() {
                    let _ = fs::write(dest, to_json(built));
                    return 0;
                }
                return 1;
            }
            None => return 1,
        }
    }
}

#[allow(dead_code)]
fn _touch_get_mut(n: &mut Node) {
    let _ = map_get_mut(n, "kind");
}
