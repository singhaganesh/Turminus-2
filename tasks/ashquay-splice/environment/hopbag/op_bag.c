#include "op_bag.h"
#include "readwell.h"

#include <string.h>

int op_bag(const char *a, char b[][64], int c) {
  char hosts[8][64];
  int ranks[8];
  char roots[8][256];
  int n = load_cards(hosts, ranks, roots, 8);
  int i, j;
  int idx = 0;
  for (i = 0; i < n; i++) {
    for (j = i + 1; j < n; j++) {
      if (strcmp(hosts[j], hosts[i]) < 0) {
        char th[64];
        char tr[256];
        int tk = ranks[i];
        memcpy(th, hosts[i], 64);
        memcpy(hosts[i], hosts[j], 64);
        memcpy(hosts[j], th, 64);
        memcpy(tr, roots[i], 256);
        memcpy(roots[i], roots[j], 256);
        memcpy(roots[j], tr, 256);
        ranks[i] = ranks[j];
        ranks[j] = tk;
      }
    }
  }
  if (a && strchr(a, 'A') != NULL) {
    idx = 1;
  }
  if (n <= 0 || c <= 0) {
    return 0;
  }
  strncpy(b[0], hosts[idx % n], 63);
  b[0][63] = 0;
  return 1;
}
