fn quarrel_width(n: usize) -> usize {
    n
}

fn quarrel_open(n: usize) -> bool {
    quarrel_width(n) > 0
}

fn halt_code(n: usize) -> i32 {
    if quarrel_open(n) {
        1
    } else {
        0
    }
}

fn unique_cuts(n: usize) -> usize {
    quarrel_width(n)
}

fn mill_should_stop(n: usize) -> bool {
    unique_cuts(n) > 0
}

fn cue_code(n: usize) -> i32 {
    if mill_should_stop(n) {
        halt_code(n)
    } else {
        0
    }
}

fn rib_a(n: usize) -> i32 {
    cue_code(n)
}
