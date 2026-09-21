#include "../knothub/store.h"
#include "../readcue/scan.h"
#include "../inkurn/book.h"
#include "../knothub/graph.h"
#include "../knothub/pick.h"
#include "../emiturn/bind.h"
#include "rank.h"

#include <stdio.h>
#include <string.h>

int assay_run(const char *dump, const char *out) {
  snprintf(g_path, sizeof g_path, "%s", dump);
  if (scan_dump(dump) != 0) {
    return 2;
  }
  if (book_load("/app/inkurn/book.tsv") != 0) {
    return 2;
  }
  graph_build();
  op_pick();
  rk_wrap();
  return n_bind(out);
}
