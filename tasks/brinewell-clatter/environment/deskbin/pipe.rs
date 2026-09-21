use std::fs;

pub fn fill() -> i32 {
    match crate::walk::rib_a() {
        Err(c) => {
            let _ = fs::remove_file("/app/kegbay/MARK");
            c
        }
        Ok(names) => {
            let pairs = crate::stamp::rib_b(&names);
            fs::create_dir_all("/app/kegbay").ok();
            let mut body = String::new();
            for (n, k) in pairs {
                body.push_str(&format!("{}\t{}\n", n, k));
            }
            fs::write("/app/kegbay/pairs.tmp", body).ok();
            0
        }
    }
}
