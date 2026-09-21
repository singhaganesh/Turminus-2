#include "../knothub/store.h"
#include "../readcue/scan.h"
#include "../inkurn/book.h"
#include "../knothub/graph.h"
#include "../inkfold/fold.h"

#include <stdio.h>
#include <string.h>

int assay_run(const char *dump, const char *out);

int main(int argc, char **argv) {
  if (argc < 2) {
    fputs("usage\n", stderr);
    return 2;
  }
  if (strcmp(argv[1], "unjam") == 0 && argc >= 4) {
    return assay_run(argv[2], argv[3]);
  }
  if (strcmp(argv[1], "scroll") == 0 && argc >= 4) {
    snprintf(g_path, sizeof g_path, "%s", argv[2]);
    if (scan_dump(argv[2]) != 0) {
      return 2;
    }
    return cfg_fold(argv[3]);
  }
  if (strcmp(argv[1], "roster") == 0 && argc >= 3) {
    if (scan_dump(argv[2]) != 0) {
      return 2;
    }
    if (book_load("/app/inkurn/book.tsv") != 0) {
      return 2;
    }
    graph_build();
    roster_out();
    return 0;
  }
  fputs("usage\n", stderr);
  return 2;
}
