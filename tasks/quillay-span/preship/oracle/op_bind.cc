#include "bind.h"

#include "elfbits.h"
#include "sum.h"

#include <ctype.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>

static void fold_hex(char *s) {
  for (; *s; s++) {
    if (*s >= 'A' && *s <= 'F') *s = (char)(*s - 'A' + 'a');
  }
}

static int magic_ok(const char *path) {
  FILE *fp = fopen(path, "rb");
  if (!fp) return 0;
  unsigned char m[4];
  size_t n = fread(m, 1, 4, fp);
  fclose(fp);
  return n == 4 && m[0] == 0x7f && m[1] == 'E' && m[2] == 'L' && m[3] == 'F';
}

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
  memset(b, 0, sizeof(*b));
  memcpy(b->path, path, sizeof(b->path) - 1);
  b->dev = dev;
  b->ino = ino;
  b->vma = vma;
  b->off = off;
  b->sz = sz;
  return 1;
}

static int write_row(const struct Lay *b) {
  if (!b->path[0]) return -1;
  FILE *fp = fopen("/app/wickbin/layout.qmap", "w");
  if (!fp) return -1;
  fprintf(fp, "QMAP1\n");
  fprintf(fp, "%s %llu %llu %llu %llu %llu\n", b->path, b->dev, b->ino, b->vma, b->off, b->sz);
  fclose(fp);
  return 0;
}

static int load_mark(char *hex, size_t n) {
  FILE *fp = fopen("/app/wickbin/clock.txt", "r");
  if (!fp) return 0;
  memset(hex, 0, n);
  if (!fgets(hex, (int)n, fp)) {
    fclose(fp);
    return 0;
  }
  fclose(fp);
  for (char *p = hex; *p; p++) {
    if (*p == '\n') *p = 0;
  }
  fold_hex(hex);
  return (int)strlen(hex) == 64;
}

static int save_mark(const char *hex) {
  FILE *fp = fopen("/app/wickbin/clock.txt", "w");
  if (!fp) return -1;
  fprintf(fp, "%s\n", hex);
  fclose(fp);
  return 0;
}

int op_bind(const char *a, struct Lay *b) {
  if (!a || !b) return -1;
  if (!magic_ok(a)) return -1;
  struct stat st;
  if (stat(a, &st) != 0) return -1;
  struct Lay old;
  memset(&old, 0, sizeof(old));
  int have = read_row(&old);
  memset(b, 0, sizeof(*b));
  memcpy(b->path, a, sizeof(b->path) - 1);
  b->dev = (unsigned long long)st.st_dev;
  b->ino = (unsigned long long)st.st_ino;
  char hex[65];
  memset(hex, 0, sizeof(hex));
  if (file_sha256_hex(a, hex) != 0) return -1;
  fold_hex(hex);
  memcpy(b->dig, hex, 64);
  b->dig[64] = 0;
  if (fill_text(a, &b->vma, &b->off, &b->sz) != 0) return -1;
  if (b->sz == 0) return -1;
  if (write_row(b) != 0) return -1;
  char prior[65];
  memset(prior, 0, sizeof(prior));
  int marked = load_mark(prior, sizeof(prior));
  if (save_mark(hex) != 0) return -1;
  if (have && old.dev == b->dev && old.ino == b->ino && marked && strcmp(prior, hex) == 0)
    return 1;
  return 0;
}
