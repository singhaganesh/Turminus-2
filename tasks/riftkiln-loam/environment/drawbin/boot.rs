include!("../ribjoin/cursor.rs");

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 4 || args[1] != "sift" {
        eprintln!("usage: riftkiln sift SRC DEST");
        std::process::exit(2);
    }
    let rc = run_sift(&args[2], &args[3]);
    std::process::exit(rc);
}
