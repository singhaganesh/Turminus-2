#include "graph.h"
#include "store.h"

#include <string.h>

static int find_hex(const char *hx) {
  for (int i = 0; i < GN; i++) {
    if (strcmp(G[i].hex, hx) == 0) {
      return i;
    }
  }
  return -1;
}

void graph_build(void) {
  memset(succ, 0, sizeof succ);
  memset(nsucc, 0, sizeof nsucc);
  for (int i = 0; i < GN; i++) {
    G[i].indeg = 0;
    G[i].done = 0;
  }
  for (int i = 0; i < GN; i++) {
    int w;
    if (!G[i].has_wait) {
      continue;
    }
    w = find_hex(G[i].wait_hex);
    if (w < 0) {
      continue;
    }
    /* w precedes i */
    succ[w][nsucc[w]++] = i;
    G[i].indeg++;
  }
}
