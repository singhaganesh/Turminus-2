#[path = "../urncue/fold.rs"]
mod fold;
#[path = "../millrib/gait.rs"]
mod gait;
#[path = "../lidcue/skip.rs"]
mod skip;
#[path = "../corkpit/floor.rs"]
mod floor;

fn main() {
    let mut args = std::env::args();
    let _ = args.next();
    let cmd = args.next().unwrap_or_default();
    if cmd != "clasp" {
        eprintln!("usage: dewkiln clasp");
        std::process::exit(2);
    }
    let _ = std::fs::remove_file("/app/bloturn/GUARD");
    let code = match fold::fold() {
        Ok((packed, taken)) => {
            let mut dump = packed.clone();
            skip::skip(&mut dump);
            let _ = floor::floor(taken);
            gait::gait(taken, &packed)
        }
        Err(c) => c,
    };
    std::process::exit(code);
}
