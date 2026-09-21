#include "n_credit.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void read_first(char *out, int n) {
  FILE *f = fopen("/app/mill.cfg", "r");
  char line[128];
  strncpy(out, "fastpit", (size_t)n - 1);
  out[n - 1] = 0;
  if (!f) {
    return;
  }
  while (fgets(line, sizeof(line), f)) {
    char *nl = strchr(line, '\n');
    if (nl) {
      *nl = 0;
    }
    if (strncmp(line, "retry_first=", 12) == 0) {
      strncpy(out, line + 12, (size_t)n - 1);
      out[n - 1] = 0;
    }
  }
  fclose(f);
}

int n_credit(const char *a, const struct Sel *b, int c) {
  char path[320];
  char first[64];
  FILE *f;
  int i, j;
  int n = 0;
  Sel tmp[8];
  if (!a || c < 0) {
    return 1;
  }
  snprintf(path, sizeof(path), "%s/provenance.json", a);
  f = fopen(path, "w");
  if (!f) {
    return 1;
  }
  read_first(first, 64);
  for (i = 0; i < c; i++) {
    if (b[i].bid[0] == 0) {
      continue;
    }
    tmp[n] = b[i];
    if (tmp[n].host[0] == 0) {
      strncpy(tmp[n].host, first, 63);
      tmp[n].host[63] = 0;
    }
    n++;
  }
  for (i = 0; i < n; i++) {
    for (j = i + 1; j < n; j++) {
      if (strcmp(tmp[j].bid, tmp[i].bid) < 0) {
        Sel t = tmp[i];
        tmp[i] = tmp[j];
        tmp[j] = t;
      }
    }
  }
  fprintf(f, "{\"objects\":[");
  for (i = 0; i < n; i++) {
    if (i) {
      fputc(',', f);
    }
    fprintf(f, "{\"build_id\":\"%s\",\"host\":\"%s\"}", tmp[i].bid, tmp[i].host);
  }
  fprintf(f, "]}\n");
  fclose(f);
  return 0;
}
