#ifndef STORE_H
#define STORE_H

#include <stdint.h>

#define MAXL 64

typedef struct {
  char hex[40];
  char wait_hex[40];
  uint32_t tag;
  uint32_t wait_tag;
  uint32_t tid;
  int has_wait;
  int indeg;
  int done;
  int depth;
} LockRec;

extern LockRec G[MAXL];
extern int GN;
extern int g_closer;
extern int PLAN[MAXL];
extern int PN;
extern int succ[MAXL][MAXL];
extern int nsucc[MAXL];
extern char g_path[256];

int scan_dump(const char *path);
int book_load(const char *path);
void graph_build(void);
void roster_out(void);
void rk_wrap(void);
int assay_run(const char *dump, const char *out);

#endif
