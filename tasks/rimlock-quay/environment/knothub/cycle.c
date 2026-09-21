#include "store.h"
#include "../inkurn/book.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int cmp_u(const void *a, const void *b) {
  uint32_t x = *(const uint32_t *)a;
  uint32_t y = *(const uint32_t *)b;
  if (x < y) {
    return -1;
  }
  if (x > y) {
    return 1;
  }
  return 0;
}

void roster_out(void) {
  uint32_t cyc[MAXL];
  int cn = 0;
  int seen[MAXL];

  memset(seen, 0, sizeof seen);
  for (int i = 0; i < GN; i++) {
    if (G[i].has_wait) {
      int w = -1;
      for (int j = 0; j < GN; j++) {
        if (strcmp(G[j].hex, G[i].wait_hex) == 0) {
          w = j;
          break;
        }
      }
      if (w >= 0 && G[w].has_wait && strcmp(G[w].wait_hex, G[i].hex) == 0) {
        if (!seen[i]) {
          cyc[cn++] = G[i].tag;
          seen[i] = 1;
        }
        if (!seen[w]) {
          cyc[cn++] = G[w].tag;
          seen[w] = 1;
        }
      }
    }
  }
  qsort(cyc, (size_t)cn, sizeof cyc[0], cmp_u);
  fputs("CYCLE", stdout);
  for (int i = 0; i < cn; i++) {
    printf(" %u", cyc[i]);
  }
  fputc('\n', stdout);
  for (int i = 0; i < GN; i++) {
    printf("OWNER %u=%u\n", G[i].tag, G[i].tid);
  }
}
