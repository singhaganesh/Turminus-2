#!/bin/bash
set -euo pipefail
sed -i 's/pub const ROOM: usize = 65536;/pub const ROOM: usize = 262144;/' /app/slipcards/cap.rs
/app/hull.sh
