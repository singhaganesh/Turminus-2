pub struct Pack {
    pub t: String,
    pub c: String,
    pub e: Vec<String>,
    pub n: u32,
    pub s: String,
    pub w: String,
}

struct Rec {
    name: String,
    hdr: u64,
    size: u64,
    body: u64,
}

fn read_idx(path: &str) -> Result<Vec<Rec>, i32> {
    let raw = std::fs::read(path).map_err(|_| 1)?;
    if raw.len() < 9 || &raw[0..5] != b"SILT1" {
        return Err(1);
    }
    let n = u32::from_le_bytes(raw[5..9].try_into().unwrap());
    let mut i = 9usize;
    let mut out = Vec::new();
    for _ in 0..n {
        if i + 26 > raw.len() {
            return Err(1);
        }
        let hdr = u64::from_le_bytes(raw[i..i + 8].try_into().unwrap());
        i += 8;
        let size = u64::from_le_bytes(raw[i..i + 8].try_into().unwrap());
        i += 8;
        let body = u64::from_le_bytes(raw[i..i + 8].try_into().unwrap());
        i += 8;
        let nl = u16::from_le_bytes(raw[i..i + 2].try_into().unwrap()) as usize;
        i += 2;
        if i + nl > raw.len() {
            return Err(1);
        }
        let name = String::from_utf8_lossy(&raw[i..i + nl]).to_string();
        i += nl;
        out.push(Rec {
            name,
            hdr,
            size,
            body,
        });
    }
    Ok(out)
}

fn load(path: &str, body: u64, size: u64) -> Result<Vec<u8>, i32> {
    let raw = std::fs::read(path).map_err(|_| 1)?;
    let s = body as usize;
    let e = s + size as usize;
    if e > raw.len() {
        return Err(1);
    }
    Ok(raw[s..e].to_vec())
}

fn digest(text: &str) -> String {
    let mut cmd = std::process::Command::new("python3");
    cmd.args([
        "-c",
        "import hashlib,sys; print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest())",
    ])
    .stdin(std::process::Stdio::piped())
    .stdout(std::process::Stdio::piped());
    let mut child = match cmd.spawn() {
        Ok(c) => c,
        Err(_) => return String::new(),
    };
    {
        use std::io::Write;
        if let Some(ref mut sin) = child.stdin {
            let _ = sin.write_all(text.as_bytes());
        }
    }
    drop(child.stdin.take());
    match child.wait_with_output() {
        Ok(out) => String::from_utf8_lossy(&out.stdout).trim().to_string(),
        Err(_) => String::new(),
    }
}

#[path = "../keeppit/first.rs"]
mod first;
#[path = "../cfgbag/kv.rs"]
mod kv;
#[path = "../cfgbag/alias.rs"]
mod alias;

pub fn rib_b(a: &str, b: &str) -> Result<Pack, i32> {
    let recs = read_idx(b)?;
    let mut confs: Vec<(String, u64, Vec<u8>)> = Vec::new();
    let mut logs: Vec<Vec<u8>> = Vec::new();
    let mut bag: std::collections::HashMap<usize, String> = std::collections::HashMap::new();
    for (i, r) in recs.iter().enumerate() {
        bag.insert(i, r.name.clone());
        let blob = load(a, r.body, r.size)?;
        if r.name.contains("sys.conf") {
            confs.push((r.name.clone(), r.hdr, blob));
        } else if r.name.contains("app.log") {
            logs.push(blob);
        }
    }
    confs.sort_by_key(|row| row.1);
    let picked = first::keep_head(&confs);
    let mut t = String::new();
    let mut c = String::new();
    if let Some(blob) = picked {
        let map = kv::pairs(&blob);
        if let Some(v) = map.get("timezone") {
            t = v.clone();
        }
        if let Some(v) = map.get("cluster") {
            c = v.clone();
        }
    }
    let mut e = Vec::new();
    if let Some(blob) = logs.first() {
        for line in String::from_utf8_lossy(blob).lines() {
            let s = line.trim();
            if !s.is_empty() {
                e.push(s.to_string());
            }
        }
    }
    e.sort();
    e.dedup();
    let names: Vec<String> = bag.values().cloned().collect();
    let walk = names.join("\n");
    let _ = alias::fold("");
    Ok(Pack {
        t,
        c,
        e,
        n: confs.len() as u32,
        s: a.to_string(),
        w: digest(&walk).to_ascii_uppercase(),
    })
}
