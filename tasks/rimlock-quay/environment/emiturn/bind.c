#include "bind.h"
#include "../knothub/store.h"

#include <stdio.h>
#include <string.h>

static const char *wire_token(const LockRec *r) {
  return r->hex;
}

static void dir_of(const char *a, char *dir, size_t cap) {
  const char *slash = strrchr(a, '/');
  if (!slash) {
    snprintf(dir, cap, ".");
    return;
  }
  size_t n = (size_t)(slash - a);
  if (n >= cap) {
    n = cap - 1;
  }
  memcpy(dir, a, n);
  dir[n] = 0;
}

int n_bind(const char *a) {
  FILE *f;
  FILE *ok;
  char dir[128];
  char okp[160];
  int i;

  dir_of(a, dir, sizeof dir);
  snprintf(okp, sizeof okp, "%s/mill.ok", dir);

  f = fopen(a, "w");
  if (!f) {
    return 2;
  }
  for (i = 0; i < PN; i++) {
    int k = PLAN[i];
    fprintf(f, "%s\n", wire_token(&G[k]));
  }
  fclose(f);

  if (GN > 0) {
    ok = fopen(okp, "w");
    if (ok) {
      fputs("ok\n", ok);
      fclose(ok);
    }
  }
  return 0;
}
