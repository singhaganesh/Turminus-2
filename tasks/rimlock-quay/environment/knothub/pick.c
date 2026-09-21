#include "pick.h"
#include "store.h"

int op_pick(void) {
  int q[MAXL];
  int enq[MAXL];
  int qh = 0;
  int qt = 0;
  int i;

  PN = 0;
  for (i = 0; i < GN; i++) {
    enq[i] = 0;
  }
  for (i = 0; i < GN; i++) {
    if (G[i].indeg == 0) {
      q[qt++] = i;
      enq[i] = 1;
    }
  }
  while (qh < qt) {
    int cur = q[qh++];
    int k;
    if (G[cur].done) {
      continue;
    }
    PLAN[PN++] = cur;
    G[cur].done = 1;
    for (k = 0; k < nsucc[cur]; k++) {
      int j = succ[cur][k];
      if (G[j].indeg > 0) {
        G[j].indeg--;
      }
      if (G[j].indeg == 0 && !enq[j]) {
        q[qt++] = j;
        enq[j] = 1;
      }
    }
  }
  for (i = 0; i < GN; i++) {
    if (!G[i].done) {
      PLAN[PN++] = i;
      G[i].done = 1;
    }
  }
  return 0;
}
