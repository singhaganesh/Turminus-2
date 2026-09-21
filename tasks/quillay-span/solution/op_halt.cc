#include "halt.h"

#include "sum.h"

#include <ctype.h>
#include <stdio.h>
#include <string.h>

static void fold_hex(char *s) {
  for (; *s; s++) {
    if (*s >= 'A' && *s <= 'F') *s = (char)(*s - 'A' + 'a');
  }
}

static int hex64(const char *s) {
  int n = 0;
  for (; s[n]; n++) {
    char c = s[n];
    if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F')))
      return 0;
  }
  return n == 64;
}

int op_halt(void) {
  FILE *fp = fopen("/app/wickbin/layout.qmap", "r");
  if (!fp) return 1;
  char hdr[32];
  if (!fgets(hdr, sizeof(hdr), fp)) {
    fclose(fp);
    return 1;
  }
  if (strncmp(hdr, "QMAP1", 5) != 0) {
    fclose(fp);
    return 1;
  }
  int dirty = 0;
  char line[512];
  int rows = 0;
  while (fgets(line, sizeof(line), fp)) {
    if (line[0] == '\n' || line[0] == '#') continue;
    char path[256];
    unsigned long long dev = 0, ino = 0, vma = 0, off = 0, sz = 0;
    memset(path, 0, sizeof(path));
    if (sscanf(line, "%255s %llu %llu %llu %llu %llu", path, &dev, &ino, &vma, &off, &sz) != 6) {
      dirty = 1;
      break;
    }
    (void)dev;
    (void)ino;
    (void)vma;
    (void)off;
    (void)sz;
    char mark[65];
    memset(mark, 0, sizeof(mark));
    FILE *ck = fopen("/app/wickbin/clock.txt", "r");
    if (!ck) {
      dirty = 1;
      break;
    }
    if (!fgets(mark, sizeof(mark), ck)) {
      fclose(ck);
      dirty = 1;
      break;
    }
    fclose(ck);
    for (char *p = mark; *p; p++) {
      if (*p == '\n') *p = 0;
    }
    fold_hex(mark);
    if (!hex64(mark)) {
      dirty = 1;
      break;
    }
    char hex[65];
    memset(hex, 0, sizeof(hex));
    if (file_sha256_hex(path, hex) != 0) {
      dirty = 1;
      break;
    }
    fold_hex(hex);
    if (strcmp(hex, mark) != 0) dirty = 1;
    rows++;
  }
  fclose(fp);
  if (rows < 1) return 1;
  return dirty ? 1 : 0;
}
