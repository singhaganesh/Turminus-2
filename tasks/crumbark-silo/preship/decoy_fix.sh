#!/bin/bash
set -euo pipefail
cat > /app/retrycue/PauseCue.java << 'EOF'
public class PauseCue {
    public static void nap() {
        try {
            Thread.sleep(200L);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
EOF
/app/brimvat.sh
