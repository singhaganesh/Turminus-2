#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd /app
cat > /app/knothub/pick.c <<'ENDPICK'
#include "pick.h"
#include "store.h"

static int tag_lt(int a, int b) {
  if (G[a].tag < G[b].tag) {
    return 1;
  }
  if (G[a].tag > G[b].tag) {
    return 0;
  }
  return G[a].tid < G[b].tid;
}

static void dec_succ(int best) {
  int k;
  for (k = 0; k < nsucc[best]; k++) {
    int j = succ[best][k];
    if (G[j].indeg > 0) {
      G[j].indeg--;
    }
  }
}

static int min_ready(int need_zero) {
  int best = -1;
  int i;
  for (i = 0; i < GN; i++) {
    if (G[i].done) {
      continue;
    }
    if (need_zero && G[i].indeg != 0) {
      continue;
    }
    if (best < 0 || tag_lt(i, best)) {
      best = i;
    }
  }
  return best;
}

static int remain_count(void) {
  int i;
  int n = 0;
  for (i = 0; i < GN; i++) {
    if (!G[i].done) {
      n++;
    }
  }
  return n;
}

int op_pick(void) {
  int guard = 0;
  PN = 0;
  while (guard < MAXL && remain_count() > 0) {
    int best = min_ready(1);
    if (best < 0) {
      best = min_ready(0);
    }
    if (best < 0) {
      break;
    }
    PLAN[PN++] = best;
    G[best].done = 1;
    dec_succ(best);
    guard++;
  }
  return 0;
}
ENDPICK
cat > /app/emiturn/bind.c <<'ENDBIND'
#include "bind.h"
#include "../knothub/store.h"

#include <stdio.h>
#include <string.h>
#include <unistd.h>

static void dir_of(const char *a, char *dir, size_t cap) {
  const char *slash = strrchr(a, '/');
  if (!slash) {
    snprintf(dir, cap, ".");
    return;
  }
  size_t n = (size_t)(slash - a);
  if (n >= cap) {
    n = cap - 1;
  }
  memcpy(dir, a, n);
  dir[n] = 0;
}

static int emit_tags(FILE *f) {
  int i;
  for (i = 0; i < PN; i++) {
    int k = PLAN[i];
    if (fprintf(f, "%u\n", G[k].tag) < 0) {
      return 2;
    }
  }
  return 0;
}

static int stamp_ok(const char *okp) {
  FILE *ok = fopen(okp, "w");
  if (!ok) {
    return 2;
  }
  fputs("ok\n", ok);
  fclose(ok);
  return 0;
}

int n_bind(const char *a) {
  FILE *f;
  char dir[128];
  char okp[160];

  dir_of(a, dir, sizeof dir);
  snprintf(okp, sizeof okp, "%s/mill.ok", dir);

  if (!g_closer) {
    unlink(okp);
    return 2;
  }

  f = fopen(a, "w");
  if (!f) {
    return 2;
  }
  if (emit_tags(f) != 0) {
    fclose(f);
    return 2;
  }
  fclose(f);
  return stamp_ok(okp);
}
ENDBIND
cat > /app/inkfold/fold.c <<'ENDFOLD'
#include "fold.h"
#include "../knothub/store.h"
#include "../readcue/scan.h"
#include "../inkurn/book.h"
#include "../knothub/graph.h"
#include "../knothub/pick.h"
#include "../hullcue/rank.h"

#include <stdio.h>
#include <string.h>

static int load_graph(void) {
  if (GN == 0 && g_path[0]) {
    if (scan_dump(g_path) != 0) {
      return 2;
    }
  }
  if (book_load("/app/inkurn/book.tsv") != 0) {
    return 2;
  }
  graph_build();
  op_pick();
  rk_wrap();
  return 0;
}

static int emit_rows(FILE *f) {
  int i;
  for (i = 0; i < PN; i++) {
    int k = PLAN[i];
    if (fprintf(f, "%u %u\n", G[k].tid, G[k].tag) < 0) {
      return 2;
    }
  }
  return 0;
}

int cfg_fold(const char *a) {
  FILE *f;

  if (load_graph() != 0) {
    return 2;
  }

  f = fopen(a, "w");
  if (!f) {
    return 2;
  }
  if (emit_rows(f) != 0) {
    fclose(f);
    return 2;
  }
  fclose(f);
  return 0;
}
ENDFOLD
rm -f /app/knothub/*.rej /app/emiturn/*.rej /app/inkfold/*.rej
chmod +x /app/stoke.sh
/app/stoke.sh
mkdir -p /app/planbay /app/scrollbay
/app/bin/rimlock unjam /app/vatdock/shift.dmp /app/planbay/live.plan
/app/bin/rimlock unjam /app/vatdock/dusk.dmp /app/planbay/alt.plan
/app/bin/rimlock scroll /app/vatdock/shift.dmp /app/scrollbay/desk.chk
