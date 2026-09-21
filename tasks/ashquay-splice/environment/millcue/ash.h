#ifndef ASH_H
#define ASH_H

#include "readwell.h"

typedef struct Ctx {
  char core[256];
  char out[256];
  Obj objs[8];
  int nobj;
  char sel_bid[8][32];
  char sel_host[8][64];
  int nsel;
  char frames[64][160];
  int nfr;
} Ctx;

int run_go(Ctx *x);
int run_fin(Ctx *x);

#endif
