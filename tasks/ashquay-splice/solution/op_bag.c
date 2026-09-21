#include "op_bag.h"
#include "readwell.h"

#include <string.h>

static void swap_row(char hosts[][64], int ranks[], char roots[][256], int i, int j) {
  char th[64];
  char tr[256];
  int tk;
  memcpy(th, hosts[i], 64);
  memcpy(hosts[i], hosts[j], 64);
  memcpy(hosts[j], th, 64);
  memcpy(tr, roots[i], 256);
  memcpy(roots[i], roots[j], 256);
  memcpy(roots[j], tr, 256);
  tk = ranks[i];
  ranks[i] = ranks[j];
  ranks[j] = tk;
}

int op_bag(const char *a, char b[][64], int c) {
  char hosts[8][64];
  int ranks[8];
  char roots[8][256];
  int n = load_cards(hosts, ranks, roots, 8);
  int i, j, out = 0;
  (void)a;
  if (n <= 0 || c <= 0) {
    return 0;
  }
  for (i = 0; i < n; i++) {
    for (j = i + 1; j < n; j++) {
      if (ranks[j] < ranks[i]) {
        swap_row(hosts, ranks, roots, i, j);
      } else if (ranks[j] == ranks[i] && strcmp(hosts[j], hosts[i]) < 0) {
        swap_row(hosts, ranks, roots, i, j);
      }
    }
  }
  for (i = 0; i < n && out < c; i++) {
    if (!hosts[i][0]) {
      continue;
    }
    if (!roots[i][0]) {
      continue;
    }
    strncpy(b[out], hosts[i], 63);
    b[out][63] = 0;
    out++;
  }
  return out;
}
