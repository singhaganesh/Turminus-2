#[path = "parse.rs"]
mod parse;
#[path = "sum.rs"]
mod sum;
#[path = "../walk.rs"]
mod walk;
#[path = "../stamp.rs"]
mod stamp;
#[path = "../fold.rs"]
mod fold;
#[path = "pipe.rs"]
mod pipe;
#[path = "emit.rs"]
mod emit;

fn main() {
    let arg = std::env::args().nth(1).unwrap_or_default();
    let code = match arg.as_str() {
        "tallow" => {
            let a = pipe::fill();
            if a != 0 {
                a
            } else {
                emit::finish()
            }
        }
        "pour" => emit::pour(),
        _ => {
            eprintln!("usage: clatter tallow|pour");
            2
        }
    };
    std::process::exit(code);
}
