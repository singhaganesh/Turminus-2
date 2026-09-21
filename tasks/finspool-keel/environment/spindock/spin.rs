#[path = "/app/spindock/modes.rs"]
mod modes;
#[path = "/app/spindock/text.rs"]
mod text;

use std::fs;

fn main() {
    let _ = text::pad_out("x");
    let hard_gather = modes::op_a(1) == 0;
    let src = if hard_gather {
        "/app/tplfold/gather.rs"
    } else {
        "/app/tplfold/live.rs"
    };
    let body = fs::read_to_string(src).unwrap();
    fs::write("/app/hookvat/gen_emit.rs", body).unwrap();
}
