#include "halt.h"

int go_scribe(void);

#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#include "stamp.h"

static int do_knit(void) {
  FILE *wf = fopen("/app/spanhearth/wave.txt", "r");
  int wave = 1;
  if (wf) {
    fscanf(wf, "%d", &wave);
    fclose(wf);
  }
  char cmd[256];
  snprintf(cmd, sizeof(cmd),
           "gcc -no-pie -fno-pie -O0 -DWAVE=%d -o /tmp/span.new /app/spanhearth/load.c",
           wave);
  if (system(cmd) != 0) return 1;
  FILE *in = fopen("/tmp/span.new", "rb");
  FILE *out = fopen("/app/hearthbin/span.elf", "r+b");
  if (!out) {
    out = fopen("/app/hearthbin/span.elf", "wb");
  }
  if (!in || !out) {
    if (in) fclose(in);
    if (out) fclose(out);
    return 1;
  }
  char buf[4096];
  size_t n;
  long total = 0;
  rewind(out);
  while ((n = fread(buf, 1, sizeof(buf), in)) > 0) {
    if (fwrite(buf, 1, n, out) != n) {
      fclose(in);
      fclose(out);
      return 1;
    }
    total += (long)n;
  }
  fclose(in);
  if (ftruncate(fileno(out), total) != 0) {
    fclose(out);
    return 1;
  }
  fclose(out);
  chmod("/app/hearthbin/span.elf", 0755);
  stamp_zero("/app/hearthbin/span.elf");
  FILE *nm = popen("nm -P /app/hearthbin/span.elf", "r");
  FILE *pc = fopen("/app/spanhearth/pc.lst", "w");
  if (!nm || !pc) return 1;
  char line[256];
  while (fgets(line, sizeof(line), nm)) {
    char name[128], typ[8];
    unsigned long long addr = 0, sz = 0;
    if (sscanf(line, "%127s %7s %llx %llx", name, typ, &addr, &sz) >= 3) {
      if (strcmp(name, "ring_pump") == 0 || strcmp(name, "dusk_lamp") == 0 ||
          strcmp(name, "held_wick") == 0) {
        fprintf(pc, "%llx\n", addr);
      }
    }
  }
  pclose(nm);
  fclose(pc);
  return 0;
}

int main(int argc, char **argv) {
  if (argc < 2) return 2;
  if (strcmp(argv[1], "tamp") == 0) return do_knit();
  if (strcmp(argv[1], "scribe") == 0) return go_scribe();
  if (strcmp(argv[1], "weigh") == 0) return op_halt();
  return 2;
}
