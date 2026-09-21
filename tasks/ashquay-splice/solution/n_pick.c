#include "n_pick.h"

static int better(const struct Obj *x, const struct Obj *y) {
  if (x->n_line != y->n_line) {
    return x->n_line > y->n_line;
  }
  if (x->n_sym != y->n_sym) {
    return x->n_sym > y->n_sym;
  }
  if (x->rank != y->rank) {
    return x->rank < y->rank;
  }
  return 0;
}

int n_pick(const struct Obj *a, int b) {
  int best = 0;
  int i;
  int saw = 0;
  if (b <= 0 || !a) {
    return -1;
  }
  for (i = 0; i < b; i++) {
    if (a[i].bid[0] == 0 && a[i].n_sym == 0 && a[i].n_line == 0) {
      continue;
    }
    if (!saw) {
      best = i;
      saw = 1;
      continue;
    }
    if (better(&a[i], &a[best])) {
      best = i;
    }
  }
  if (!saw) {
    return -1;
  }
  return best;
}
