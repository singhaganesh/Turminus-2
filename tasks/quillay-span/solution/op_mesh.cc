#include "mesh.h"

#include "elfbits.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct Pc {
  unsigned long long v;
};

static int cmp_pc(const void *x, const void *y) {
  const struct Pc *a = (const struct Pc *)x;
  const struct Pc *b = (const struct Pc *)y;
  if (a->v < b->v) return -1;
  if (a->v > b->v) return 1;
  return 0;
}

int op_mesh(const char *a, const struct Lay *b, int c) {
  (void)b;
  (void)c;
  if (!a) return -1;
  FILE *lst = fopen("/app/spanhearth/pc.lst", "r");
  if (!lst) return -1;
  struct Pc pcs[128];
  int n = 0;
  char line[128];
  while (fgets(line, sizeof(line), lst) && n < 128) {
    unsigned long long pc = 0;
    if (sscanf(line, "%llx", &pc) != 1) continue;
    if (pc == 0) continue;
    pcs[n++].v = pc;
  }
  fclose(lst);
  if (n < 1) return -1;
  qsort(pcs, (size_t)n, sizeof(pcs[0]), cmp_pc);
  FILE *out = fopen("/app/wickbin/flame.qprf", "w");
  if (!out) return -1;
  fprintf(out, "QPRF1\n");
  for (int i = 0; i < n; i++) {
    if (i > 0 && pcs[i].v == pcs[i - 1].v) continue;
    char name[128];
    memset(name, 0, sizeof(name));
    if (name_at(a, pcs[i].v, name, sizeof(name)) != 0) {
      fclose(out);
      return -1;
    }
    if (name[0] == 0 || name[0] == '?') {
      fclose(out);
      return -1;
    }
    fprintf(out, "%llx %s\n", pcs[i].v, name);
  }
  fclose(out);
  return 0;
}
