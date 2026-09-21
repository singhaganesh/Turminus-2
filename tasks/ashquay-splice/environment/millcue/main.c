#include "ash.h"

#include <stdio.h>
#include <string.h>

int main(int argc, char **argv) {
  Ctx x;
  int rc;
  memset(&x, 0, sizeof(x));
  if (argc < 4 || strcmp(argv[1], "splice") != 0) {
    fprintf(stderr, "usage: ashquay splice CORE OUTDIR\n");
    return 2;
  }
  strncpy(x.core, argv[2], 255);
  strncpy(x.out, argv[3], 255);
  rc = run_go(&x);
  if (rc != 0) {
    return rc;
  }
  return run_fin(&x);
}
