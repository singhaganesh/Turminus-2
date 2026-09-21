use std::fs;
use std::path::Path;

fn read_pairs() -> Vec<(String, u64)> {
    let raw = fs::read_to_string("/app/kegbay/pairs.tmp").unwrap_or_default();
    let mut v = Vec::new();
    for line in raw.lines() {
        let mut it = line.split('\t');
        if let (Some(n), Some(k)) = (it.next(), it.next()) {
            if let Ok(u) = k.parse::<u64>() {
                v.push((n.to_string(), u));
            }
        }
    }
    v
}

pub fn finish() -> i32 {
    let pairs = read_pairs();
    match crate::fold::rib_c(&pairs, None) {
        Err(c) => c,
        Ok(names) => {
            fs::create_dir_all("/app/kegbay").ok();
            let mut body = String::new();
            for (i, n) in names.iter().enumerate() {
                let m = crate::parse::load(n);
                body.push_str(&format!(
                    "{}\t{}\t{}\n",
                    i + 1,
                    n,
                    crate::parse::guid_hex(&m.guid)
                ));
            }
            fs::write("/app/kegbay/ribbon.txt", body).ok();
            0
        }
    }
}

pub fn pour() -> i32 {
    let arg = std::env::args().nth(2);
    let root = arg.unwrap_or_else(|| "/app/dropwell".to_string());
    match crate::fold::rib_c(&[], Some(&root)) {
        Err(c) => {
            let _ = fs::remove_file("/app/kegbay/MARK");
            return c;
        }
        Ok(_) => {}
    }
    let ribbon = fs::read_to_string("/app/kegbay/ribbon.txt").unwrap_or_default();
    let mut rows: Vec<(u32, String, String, String)> = Vec::new();
    for line in ribbon.lines() {
        let p: Vec<&str> = line.split('\t').collect();
        if p.len() < 3 {
            continue;
        }
        let seq: u32 = p[0].parse().unwrap_or(0);
        let name = p[1].to_string();
        let g = p[2].to_string();
        let digest = crate::sum::hex_file(&name);
        rows.push((seq, Path::new(&name).file_name().unwrap().to_string_lossy().to_string(), digest, g));
    }
    let n = rows.len();
    let batches = if n == 0 { 0 } else { (n + 2) / 3 };
    let mut json = String::from("{\"batch_count\":");
    json.push_str(&batches.to_string());
    json.push_str(",\"entries\":[");
    for (i, (seq, name, digest, g)) in rows.iter().enumerate() {
        if i > 0 {
            json.push(',');
        }
        json.push_str(&format!(
            "{{\"seq\":{},\"name\":\"{}\",\"digest\":\"{}\",\"guid\":\"{}\"}}",
            seq, name, digest, g
        ));
    }
    json.push_str("]}\n");
    fs::create_dir_all("/app/kegbay").ok();
    fs::write("/app/kegbay/upload.json", json).ok();
    let mut tsv = String::from("seq\tname\tdigest\tguid\n");
    for (seq, name, digest, g) in &rows {
        tsv.push_str(&format!("{}\t{}\t{}\t{}\n", seq, name, digest, g));
    }
    fs::write("/app/kegbay/batch.tsv", tsv).ok();
    fs::write("/app/kegbay/MARK", "ok").ok();
    0
}
