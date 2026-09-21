#include "scan.h"
#include "../knothub/store.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void reset_g(void) {
  memset(G, 0, sizeof(G));
  GN = 0;
  g_closer = 1;
  PN = 0;
}

int scan_dump(const char *path) {
  FILE *f;
  char line[160];
  int open = 0;

  reset_g();
  f = fopen(path, "r");
  if (!f) {
    return 2;
  }
  while (fgets(line, sizeof line, f)) {
    char *nl = strchr(line, '\n');
    if (nl) {
      *nl = 0;
    }
    if (line[0] == 0) {
      continue;
    }
    if (strncmp(line, "THREAD ", 7) == 0) {
      if (open) {
        g_closer = 0;
      }
      if (GN >= MAXL) {
        fclose(f);
        return 2;
      }
      G[GN].tid = (uint32_t)atoi(line + 7);
      open = 1;
      GN++;
      continue;
    }
    if (!open) {
      continue;
    }
    if (strncmp(line, "OWN ", 4) == 0) {
      snprintf(G[GN - 1].hex, sizeof G[GN - 1].hex, "%s", line + 4);
      continue;
    }
    if (strncmp(line, "WAIT ", 5) == 0) {
      snprintf(G[GN - 1].wait_hex, sizeof G[GN - 1].wait_hex, "%s", line + 5);
      G[GN - 1].has_wait = 1;
      continue;
    }
    if (strcmp(line, ".") == 0) {
      open = 0;
      continue;
    }
  }
  fclose(f);
  if (open) {
    g_closer = 0;
  }
  return GN > 0 ? 0 : 2;
}
