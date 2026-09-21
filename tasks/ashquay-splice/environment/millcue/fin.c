#include "ash.h"
#include "n_credit.h"

#include <stdio.h>
#include <string.h>
#include <sys/stat.h>

int run_fin(Ctx *x) {
  char path[320];
  FILE *f;
  int i;
  Sel sel[8];
  mkdir(x->out, 0755);
  snprintf(path, sizeof(path), "%s/backtrace.txt", x->out);
  f = fopen(path, "w");
  if (!f) {
    return 1;
  }
  for (i = 0; i < x->nfr; i++) {
    fprintf(f, "%s\n", x->frames[i]);
  }
  fclose(f);
  for (i = 0; i < x->nsel; i++) {
    strncpy(sel[i].bid, x->sel_bid[i], 31);
    strncpy(sel[i].host, x->sel_host[i], 63);
  }
  if (n_credit(x->out, sel, x->nsel) != 0) {
    return 1;
  }
  snprintf(path, sizeof(path), "%s/ok.mark", x->out);
  f = fopen(path, "w");
  if (!f) {
    return 1;
  }
  fputs("ok\n", f);
  fclose(f);
  return 0;
}
