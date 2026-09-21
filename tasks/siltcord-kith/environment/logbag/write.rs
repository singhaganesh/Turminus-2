use super::blend::Pack;

fn json_escape(s: &str) -> String {
    s.replace('\\', "\\\\").replace('"', "\\\"")
}

pub fn rib_c(p: &Pack, out: &str, _a: &str) -> i32 {
    if let Some(parent) = std::path::Path::new(out).parent() {
        let _ = std::fs::create_dir_all(parent);
    }
    let ev: Vec<String> = p
        .e
        .iter()
        .map(|x| format!("\"{}\"", json_escape(x)))
        .collect();
    let body = format!(
        "{{\"timezone\":\"{}\",\"cluster\":\"{}\",\"log_events\":[{}],\"member_count\":{},\"source_kith\":\"{}\",\"walk_sig\":\"{}\"}}\n",
        json_escape(&p.t),
        json_escape(&p.c),
        ev.join(","),
        p.n,
        json_escape(&p.s),
        json_escape(&p.w)
    );
    if std::fs::write(out, body).is_err() {
        return 1;
    }
    if std::fs::write("/app/deskjson/READY", "ok\n").is_err() {
        return 1;
    }
    0
}
