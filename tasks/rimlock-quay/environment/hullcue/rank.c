#include "rank.h"
#include "../knothub/store.h"

void rk_wrap(void) {
  int q[MAXL];
  int qh = 0;
  int qt = 0;

  for (int i = 0; i < GN; i++) {
    G[i].depth = 0;
    if (!G[i].has_wait) {
      q[qt++] = i;
    }
  }
  while (qh < qt) {
    int i = q[qh++];
    for (int k = 0; k < nsucc[i]; k++) {
      int j = succ[i][k];
      int d = G[i].depth + 1;
      if (d > G[j].depth) {
        G[j].depth = d;
      }
      if (qt < MAXL * 3) {
        q[qt++] = j;
      }
    }
  }
}
