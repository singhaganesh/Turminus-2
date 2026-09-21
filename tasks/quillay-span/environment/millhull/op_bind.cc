#include "bind.h"

#include "elfbits.h"
#include "stamp.h"
#include "sum.h"

#include <stdio.h>
#include <string.h>
#include <sys/stat.h>

static int read_row(struct Lay *b) {
  FILE *fp = fopen("/app/wickbin/layout.qmap", "r");
  if (!fp) return 0;
  char line[512];
  if (!fgets(line, sizeof(line), fp)) {
    fclose(fp);
    return 0;
  }
  if (!fgets(line, sizeof(line), fp)) {
    fclose(fp);
    return 0;
  }
  fclose(fp);
  unsigned long long vma = 0, off = 0, sz = 0, dev = 0, ino = 0;
  char path[256];
  memset(path, 0, sizeof(path));
  if (sscanf(line, "%255s %llu %llu %llu %llu %llu", path, &dev, &ino, &vma, &off, &sz) != 6)
    return 0;
  strncpy(b->path, path, sizeof(b->path) - 1);
  b->dev = dev;
  b->ino = ino;
  b->vma = vma;
  b->off = off;
  b->sz = sz;
  return 1;
}

static int write_row(const struct Lay *b) {
  FILE *fp = fopen("/app/wickbin/layout.qmap", "w");
  if (!fp) return -1;
  fprintf(fp, "QMAP1\n");
  fprintf(fp, "%s %llu %llu %llu %llu %llu\n", b->path, b->dev, b->ino, b->vma, b->off, b->sz);
  fclose(fp);
  return 0;
}

int op_bind(const char *a, struct Lay *b) {
  struct stat st;
  if (stat(a, &st) != 0) return -1;
  struct Lay old;
  memset(&old, 0, sizeof(old));
  int have = read_row(&old);
  memset(b, 0, sizeof(*b));
  strncpy(b->path, a, sizeof(b->path) - 1);
  b->dev = (unsigned long long)st.st_dev;
  b->ino = (unsigned long long)st.st_ino;
  char hex[65];
  if (file_sha256_hex(a, hex) != 0) return -1;
  (void)hex;
  unsigned long long stored = 0;
  FILE *ck = fopen("/app/wickbin/clock.txt", "r");
  if (ck) {
    fscanf(ck, "%llu", &stored);
    fclose(ck);
  }
  if (have && old.dev == b->dev && old.ino == b->ino && stamp_same(a, stored)) {
    *b = old;
    strncpy(b->path, a, sizeof(b->path) - 1);
    write_row(b);
    return 1;
  }
  if (fill_text(a, &b->vma, &b->off, &b->sz) != 0) return -1;
  FILE *cw = fopen("/app/wickbin/clock.txt", "w");
  if (cw) {
    fprintf(cw, "%llu\n", stamp_sec(a));
    fclose(cw);
  }
  if (write_row(b) != 0) return -1;
  return 0;
}
