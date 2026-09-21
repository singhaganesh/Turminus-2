#include "bind.h"
#include "../knothub/store.h"

#include <stdio.h>
#include <string.h>
#include <unistd.h>

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

static int emit_tags(FILE *f) {
  int i;
  for (i = 0; i < PN; i++) {
    int k = PLAN[i];
    if (fprintf(f, "%u\n", G[k].tag) < 0) {
      return 2;
    }
  }
  return 0;
}

static int stamp_ok(const char *okp) {
  FILE *ok = fopen(okp, "w");
  if (!ok) {
    return 2;
  }
  fputs("ok\n", ok);
  fclose(ok);
  return 0;
}

int n_bind(const char *a) {
  FILE *f;
  char dir[128];
  char okp[160];

  dir_of(a, dir, sizeof dir);
  snprintf(okp, sizeof okp, "%s/mill.ok", dir);

  if (!g_closer) {
    unlink(okp);
    return 2;
  }

  f = fopen(a, "w");
  if (!f) {
    return 2;
  }
  if (emit_tags(f) != 0) {
    fclose(f);
    return 2;
  }
  fclose(f);
  return stamp_ok(okp);
}
