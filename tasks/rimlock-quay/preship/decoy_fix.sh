#!/bin/bash
set -euo pipefail
# R6: follow DEPTH.txt and sort emit by wait-depth / hex
cat > /app/hullcue/rank.c << 'EOF'
#include "rank.h"
#include "../knothub/store.h"
#include <stdlib.h>
#include <string.h>
static int cmp_hex(const void *a, const void *b) {
  int i = *(const int *)a;
  int j = *(const int *)b;
  return strcmp(G[i].hex, G[j].hex);
}
void rk_wrap(void) {
  if (PN > 1) {
    qsort(PLAN, (size_t)PN, sizeof PLAN[0], cmp_hex);
  }
}
EOF
chmod +x /app/stoke.sh
/app/stoke.sh
