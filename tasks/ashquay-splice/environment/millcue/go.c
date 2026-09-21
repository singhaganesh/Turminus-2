#include "ash.h"
#include "n_pick.h"
#include "op_bag.h"
#include "retry.h"

#include <stdio.h>
#include <string.h>

int run_go(Ctx *x) {
  char hosts[8][64];
  char mods[16][32];
  unsigned bases[16];
  unsigned pcs[64];
  int nm = 0, np = 0, nh, i, m, k;
  if (!load_core(x->core, mods, bases, &nm, pcs, &np)) {
    return 2;
  }
  nh = op_bag(x->out, hosts, 8);
  retry_touch(hosts, nh);
  x->nsel = 0;
  x->nfr = 0;
  for (m = 0; m < nm; m++) {
    Obj bag[8];
    int nb = 0;
    int pi;
    memset(bag, 0, sizeof(bag));
    for (i = 0; i < nh; i++) {
      char root[256];
      char path[400];
      int rank = well_root(hosts[i], root, 256);
      if (rank < 0) {
        continue;
      }
      snprintf(path, sizeof(path), "%s/%s.dbg", root, mods[m]);
      if (load_dbg(path, hosts[i], rank, &bag[nb])) {
        nb++;
      }
    }
    pi = n_pick(bag, nb);
    if (pi < 0) {
      return 2;
    }
    strncpy(x->sel_bid[x->nsel], bag[pi].bid, 31);
    strncpy(x->sel_host[x->nsel], bag[pi].host, 63);
    x->nsel++;
    for (k = 0; k < np; k++) {
      int s;
      const Obj *o = &bag[pi];
      int used = 0;
      for (s = 0; s < o->n_sym; s++) {
        if (o->addrs[s] == pcs[k]) {
          char line[160];
          int L;
          snprintf(line, sizeof(line), "%s at 0x%08x", o->names[s], pcs[k]);
          for (L = 0; L < o->n_line; L++) {
            if (o->laddr[L] == pcs[k]) {
              snprintf(line, sizeof(line), "%s at 0x%08x %s", o->names[s],
                       pcs[k], o->lfile[L]);
              break;
            }
          }
          if (x->nfr < 64) {
            strncpy(x->frames[x->nfr], line, 159);
            x->nfr++;
          }
          used = 1;
          break;
        }
      }
      (void)used;
    }
  }
  return 0;
}
