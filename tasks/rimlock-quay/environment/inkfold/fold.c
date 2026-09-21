#include "fold.h"
#include "../knothub/store.h"
#include "../readcue/scan.h"
#include "../inkurn/book.h"
#include "../knothub/graph.h"
#include "../knothub/pick.h"
#include "../hullcue/rank.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int cmp_wire(const void *a, const void *b) {
  int i = *(const int *)a;
  int j = *(const int *)b;
  return strcmp(G[i].hex, G[j].hex);
}

int cfg_fold(const char *a) {
  int ord[MAXL];
  int i;
  FILE *f;

  if (GN == 0 && g_path[0]) {
    if (scan_dump(g_path) != 0) {
      return 2;
    }
  }
  if (book_load("/app/inkurn/book.tsv") != 0) {
    return 2;
  }
  graph_build();
  op_pick();
  rk_wrap();

  for (i = 0; i < PN; i++) {
    ord[i] = PLAN[i];
  }
  if (PN > 1) {
    qsort(ord, (size_t)PN, sizeof ord[0], cmp_wire);
  }

  f = fopen(a, "w");
  if (!f) {
    return 2;
  }
  for (i = 0; i < PN; i++) {
    int k = ord[i];
    fprintf(f, "%u %s\n", G[k].tid, G[k].hex);
  }
  fclose(f);
  return 0;
}
