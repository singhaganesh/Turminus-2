#[path = "../urnwalk/walk.rs"]
mod walk;
#[path = "../walkcue/alpha.rs"]
mod alpha;
#[path = "../qanbox/tally.rs"]
mod tally;
#[path = "../humdock/emit.rs"]
mod rib;

fn main() {
    let mut args = std::env::args();
    let _ = args.next();
    let cmd = args.next().unwrap_or_default();
    if cmd != "bind" {
        eprintln!("usage: loomketch bind [root]");
        std::process::exit(2);
    }
    let root = args.next().unwrap_or_else(|| "/app/vatlogs".to_string());
    let code = match tally::tally(&root) {
        Ok(recs) => {
            if rib::emit(&recs) != 0 {
                1
            } else {
                0
            }
        }
        Err(c) => {
            let _ = std::fs::remove_file("/app/inkbay/GUARD");
            c
        }
    };
    std::process::exit(code);
}
