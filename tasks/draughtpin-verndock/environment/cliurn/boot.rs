#[path = "../narbay/loom.rs"]
mod loom;
#[path = "../vatrib/qat.rs"]
mod qat;
#[path = "../spanmod/skip.rs"]
mod skip;
#[path = "../lidmath/note.rs"]
mod note;

fn main() {
    let mut args = std::env::args();
    let _ = args.next();
    let cmd = args.next().unwrap_or_default();
    if cmd == "sip" {
        let dump = args.next().unwrap_or_default();
        let _ = skip::skip(&dump);
        std::process::exit(qat::qat(&dump, None));
    }
    if cmd == "mark" {
        let dump = args.next().unwrap_or_default();
        let slot = args.next().unwrap_or_default();
        let _ = note::note(&slot);
        std::process::exit(qat::qat(&dump, Some(&slot)));
    }
    eprintln!("usage: draughtpin sip DUMP | draughtpin mark DUMP SLOT");
    std::process::exit(2);
}
