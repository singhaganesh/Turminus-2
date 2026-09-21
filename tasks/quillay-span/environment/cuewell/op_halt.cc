#include "halt.h"

#include "lay.h"
#include "stamp.h"

#include <stdio.h>
#include <string.h>
#include <sys/stat.h>

int op_halt(void) {
  FILE *fp = fopen("/app/wickbin/layout.qmap", "r");
  if (!fp) return 1;
  char line[512];
  if (!fgets(line, sizeof(line), fp)) {
    fclose(fp);
    return 1;
  }
  if (!fgets(line, sizeof(line), fp)) {
    fclose(fp);
    return 1;
  }
  fclose(fp);
  char path[256];
  unsigned long long dev = 0, ino = 0, vma = 0, off = 0, sz = 0;
  if (sscanf(line, "%255s %llu %llu %llu %llu %llu", path, &dev, &ino, &vma, &off, &sz) != 6)
    return 1;
  (void)vma;
  (void)off;
  (void)sz;
  struct stat st;
  if (stat(path, &st) != 0) return 1;
  unsigned long long stored = 0;
  FILE *ck = fopen("/app/wickbin/clock.txt", "r");
  if (ck) {
    fscanf(ck, "%llu", &stored);
    fclose(ck);
  }
  if ((unsigned long long)st.st_dev == dev && (unsigned long long)st.st_ino == ino &&
      stamp_same(path, stored))
    return 0;
  return 1;
}
