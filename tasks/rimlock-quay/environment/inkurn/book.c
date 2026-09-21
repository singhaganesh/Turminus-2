#include "book.h"
#include "../knothub/store.h"

#include <stdio.h>
#include <string.h>

int book_load(const char *path) {
  FILE *f;
  char line[160];
  char hx[40];
  unsigned id;

  f = fopen(path, "r");
  if (!f) {
    return 2;
  }
  while (fgets(line, sizeof line, f)) {
    if (sscanf(line, "%39s %u", hx, &id) != 2) {
      continue;
    }
    if (hx[0] == 'h' || strcmp(hx, "hex") == 0) {
      continue;
    }
    for (int i = 0; i < GN; i++) {
      if (strcmp(G[i].hex, hx) == 0) {
        G[i].tag = id;
      }
      if (G[i].has_wait && strcmp(G[i].wait_hex, hx) == 0) {
        G[i].wait_tag = id;
      }
    }
  }
  fclose(f);
  return 0;
}
