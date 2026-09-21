#[path = "../narbay/loom.rs"]
mod loom;

fn main() {
    if loom::weave("/app/gnuverse/cask.map").is_err() {
        std::process::exit(1);
    }
}
