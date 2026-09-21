#!/bin/bash
set -euo pipefail
# Apply oracle sources but skip kindle.
python3 - << 'PY'
from pathlib import Path
Path("/app/tarnpit/Tarn.java").write_text("""public class Tarn {
    public volatile int waiting;
    public volatile int keld;
    public int copy;

    public int mira() {
        int a = keld;
        waiting = 1;
        int spins = 0;
        while (a == 0) {
            a = keld;
            if (++spins > 12000000) break;
        }
        return a;
    }
}
""")
Path("/app/hopcue/Hopper.java").write_text("""public class Hopper {
    public static void feed(Tarn t, int w) {
        t.copy = w;
        if (w == 0) {
            return;
        }
        t.keld = 2 * w + 1;
    }
}
""")
print("sources patched, kindle skipped")
PY
