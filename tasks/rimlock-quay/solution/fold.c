#include "fold.h"
#include "../knothub/store.h"
#include "../readcue/scan.h"
#include "../inkurn/book.h"
#include "../knothub/graph.h"
#include "../knothub/pick.h"
#include "../hullcue/rank.h"

#include <stdio.h>
#include <string.h>

static int load_graph(void) {
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
  return 0;
}

static int emit_rows(FILE *f) {
  int i;
  for (i = 0; i < PN; i++) {
    int k = PLAN[i];
    if (fprintf(f, "%u %u\n", G[k].tid, G[k].tag) < 0) {
      return 2;
    }
  }
  return 0;
}

int cfg_fold(const char *a) {
  FILE *f;

  if (load_graph() != 0) {
    return 2;
  }

  f = fopen(a, "w");
  if (!f) {
    return 2;
  }
  if (emit_rows(f) != 0) {
    fclose(f);
    return 2;
  }
  fclose(f);
  return 0;
}
