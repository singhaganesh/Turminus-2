use crate::hold;

pub fn rim_a(a: &hold::Sess, b: &hold::Pool) -> hold::Frost {
    let _ = b;
    hold::Frost {
        n0: a.n0,
        n1: a.n1,
        ids: a.ids.clone(),
        cells: Vec::new(),
    }
}
