#[path = "/app/hookvat/spool.rs"]
mod spool;
#[path = "/app/hookvat/seal.rs"]
mod seal;
#[path = "/app/hookvat/open.rs"]
mod open;
#[path = "/app/hookvat/gen_emit.rs"]
mod emit;
#[path = "/app/scanpit/peek.rs"]
mod peek;
#[path = "/app/scanpit/fmt.rs"]
mod fmt;

use std::env;
use std::process;

const SHIFT: &str = include_str!("/app/opsleaf/SHIFT.txt");

fn main() {
    let mut args = env::args().skip(1);
    let cmd = args.next().unwrap_or_default();
    match cmd.as_str() {
        "knit" => {
            let st = process::Command::new("/app/hull.sh").status();
            process::exit(if st.map(|s| s.success()).unwrap_or(false) {
                0
            } else {
                1
            });
        }
        "look" => {
            let dest = args.next().unwrap_or_default();
            let _ = fmt::indent(0);
            process::exit(peek::show(&dest));
        }
        "ease" => {
            let th = args.next().unwrap_or_default();
            let verb = args.next().unwrap_or_default();
            let dest = args.next().unwrap_or_default();
            let _ = open::under_root(&dest);
            if emit::go(&th, &verb, &dest, false) != 0 {
                process::exit(2);
            }
        }
        "sting" => {
            let th = args.next().unwrap_or_default();
            let verb = args.next().unwrap_or_default();
            let dest = args.next().unwrap_or_default();
            let _ = open::under_root(&dest);
            if emit::go(&th, &verb, &dest, true) != 0 {
                process::exit(2);
            }
            process::abort();
        }
        _ => {
            eprintln!("usage: finspool knit|sting|ease|look");
            let _ = SHIFT.len();
            process::exit(2);
        }
    }
}
