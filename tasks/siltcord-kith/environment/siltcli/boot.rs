#[path = "quarry.rs"]
mod quarry;
#[path = "slate.rs"]
mod slate;

fn main() {
    let mut args = std::env::args();
    let _ = args.next();
    let cmd = args.next().unwrap_or_default();
    let code = match cmd.as_str() {
        "quarry" => {
            let a = args
                .next()
                .unwrap_or_else(|| "/app/sealwell/kestrel.kith".to_string());
            let b = args
                .next()
                .unwrap_or_else(|| "/app/idxbay/members.idx".to_string());
            quarry::go(&a, &b)
        }
        "brief" => {
            let out = match args.next() {
                Some(x) => x,
                None => {
                    eprintln!("usage: siltcord brief OUT.json");
                    std::process::exit(2);
                }
            };
            let a = args
                .next()
                .unwrap_or_else(|| "/app/sealwell/kestrel.kith".to_string());
            let b = args
                .next()
                .unwrap_or_else(|| "/app/idxbay/members.idx".to_string());
            slate::go(&out, &a, &b)
        }
        _ => {
            eprintln!("usage: siltcord quarry|brief");
            2
        }
    };
    std::process::exit(code);
}
