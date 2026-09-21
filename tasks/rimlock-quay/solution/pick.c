#include "pick.h"
#include "store.h"

static int tag_lt(int a, int b) {
  if (G[a].tag < G[b].tag) {
    return 1;
  }
  if (G[a].tag > G[b].tag) {
    return 0;
  }
  return G[a].tid < G[b].tid;
}

static void dec_succ(int best) {
  int k;
  for (k = 0; k < nsucc[best]; k++) {
    int j = succ[best][k];
    if (G[j].indeg > 0) {
      G[j].indeg--;
    }
  }
}

static int min_ready(int need_zero) {
  int best = -1;
  int i;
  for (i = 0; i < GN; i++) {
    if (G[i].done) {
      continue;
    }
    if (need_zero && G[i].indeg != 0) {
      continue;
    }
    if (best < 0 || tag_lt(i, best)) {
      best = i;
    }
  }
  return best;
}

static int remain_count(void) {
  int i;
  int n = 0;
  for (i = 0; i < GN; i++) {
    if (!G[i].done) {
      n++;
    }
  }
  return n;
}

int op_pick(void) {
  int guard = 0;
  PN = 0;
  while (guard < MAXL && remain_count() > 0) {
    int best = min_ready(1);
    if (best < 0) {
      best = min_ready(0);
    }
    if (best < 0) {
      break;
    }
    PLAN[PN++] = best;
    G[best].done = 1;
    dec_succ(best);
    guard++;
  }
  return 0;
}
