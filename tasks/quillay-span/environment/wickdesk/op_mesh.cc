#include "mesh.h"

#include "elfbits.h"

#include <stdio.h>
#include <string.h>

int op_mesh(const char *a, const struct Lay *b, int c) {
  (void)a;
  (void)b;
  if (c) {
    return 0;
  }
  FILE *lst = fopen("/app/spanhearth/pc.lst", "r");
  FILE *out = fopen("/app/wickbin/flame.qprf", "w");
  if (!lst || !out) {
    if (lst) fclose(lst);
    if (out) fclose(out);
    return -1;
  }
  fprintf(out, "QPRF1\n");
  char line[128];
  while (fgets(line, sizeof(line), lst)) {
    unsigned long long pc = 0;
    if (sscanf(line, "%llx", &pc) != 1) continue;
    char name[128];
    name_at(a, pc, name, sizeof(name));
    fprintf(out, "%llx %s\n", pc, name);
  }
  fclose(lst);
  fclose(out);
  return 0;
}
