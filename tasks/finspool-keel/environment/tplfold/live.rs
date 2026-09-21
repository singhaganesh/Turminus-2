use std::io::Write;

pub fn go(nm: &str, verb: &str, dest: &str, hard: bool) -> i32 {
    let mut s = crate::spool::op_b(dest);
    let card = format!(
        "FIN1\nthread={}\nop={}\n",
        crate::fmt::keep_token(nm),
        crate::fmt::keep_token(verb)
    );
    let _ = s.write_all(card.as_bytes());
    crate::spool::clip(&mut s);
    crate::seal::op_c(&mut s);
    crate::spool::park(s);
    let _ = hard;
    0
}
