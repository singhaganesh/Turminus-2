#include "readwell.h"

#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int card_cmp_name(const void *x, const void *y) {
  return strcmp((const char *)x, (const char *)y);
}

int load_cards(char hosts[][64], int ranks[], char roots[][256], int maxn) {
  DIR *d = opendir("/app/cardurn");
  struct dirent *e;
  char names[16][64];
  int nn = 0;
  int n = 0;
  int i;
  if (!d) {
    return 0;
  }
  while ((e = readdir(d)) != NULL) {
    size_t L;
    if (e->d_name[0] == '.') {
      continue;
    }
    L = strlen(e->d_name);
    if (L < 6 || strcmp(e->d_name + L - 5, ".card") != 0) {
      continue;
    }
    if (nn < 16) {
      strncpy(names[nn], e->d_name, 63);
      names[nn][63] = 0;
      nn++;
    }
  }
  closedir(d);
  qsort(names, (size_t)nn, 64, card_cmp_name);
  for (i = 0; i < nn && n < maxn; i++) {
    char path[320];
    char line[256];
    FILE *f;
    snprintf(path, sizeof(path), "/app/cardurn/%s", names[i]);
    f = fopen(path, "r");
    if (!f) {
      continue;
    }
    hosts[n][0] = 0;
    ranks[n] = 99;
    roots[n][0] = 0;
    while (fgets(line, sizeof(line), f)) {
      char *nl = strchr(line, '\n');
      if (nl) {
        *nl = 0;
      }
      if (strncmp(line, "host=", 5) == 0) {
        strncpy(hosts[n], line + 5, 63);
        hosts[n][63] = 0;
      } else if (strncmp(line, "rank=", 5) == 0) {
        ranks[n] = atoi(line + 5);
      } else if (strncmp(line, "root=", 5) == 0) {
        strncpy(roots[n], line + 5, 255);
        roots[n][255] = 0;
      }
    }
    fclose(f);
    if (hosts[n][0]) {
      n++;
    }
  }
  return n;
}

int well_root(const char *host, char *root, int n) {
  char hosts[8][64];
  int ranks[8];
  char roots[8][256];
  int i, m = load_cards(hosts, ranks, roots, 8);
  for (i = 0; i < m; i++) {
    if (strcmp(hosts[i], host) == 0) {
      strncpy(root, roots[i], (size_t)n - 1);
      root[n - 1] = 0;
      return ranks[i];
    }
  }
  return -1;
}

int load_dbg(const char *path, const char *host, int rank, Obj *o) {
  FILE *f = fopen(path, "r");
  char line[256];
  if (!f) {
    return 0;
  }
  memset(o, 0, sizeof(*o));
  strncpy(o->host, host, 63);
  o->rank = rank;
  strncpy(o->root, path, 255);
  while (fgets(line, sizeof(line), f)) {
    char *nl = strchr(line, '\n');
    unsigned addr;
    char name[64];
    char file[80];
    if (nl) {
      *nl = 0;
    }
    if (strncmp(line, "build_id=", 9) == 0) {
      strncpy(o->bid, line + 9, 31);
      o->bid[31] = 0;
    } else if (strncmp(line, "kind=", 5) == 0) {
      continue;
    } else if (sscanf(line, "@ %x %79s", &addr, file) == 2) {
      if (o->n_line < 64) {
        o->laddr[o->n_line] = addr;
        strncpy(o->lfile[o->n_line], file, 79);
        o->n_line++;
      }
    } else if (sscanf(line, "%x %63s", &addr, name) == 2) {
      if (o->n_sym < 64) {
        o->addrs[o->n_sym] = addr;
        strncpy(o->names[o->n_sym], name, 63);
        o->n_sym++;
      }
    }
  }
  fclose(f);
  return 1;
}

int load_core(const char *path, char mods[][32], unsigned bases[], int *nm,
              unsigned pcs[], int *np) {
  FILE *f = fopen(path, "r");
  char line[256];
  *nm = 0;
  *np = 0;
  if (!f) {
    return 0;
  }
  while (fgets(line, sizeof(line), f)) {
    char *nl = strchr(line, '\n');
    char bid[32];
    unsigned v;
    if (nl) {
      *nl = 0;
    }
    if (sscanf(line, "mod %31s %x", bid, &v) == 2 && *nm < 16) {
      strncpy(mods[*nm], bid, 31);
      bases[*nm] = v;
      (*nm)++;
    } else if (sscanf(line, "pc %x", &v) == 1 && *np < 64) {
      pcs[*np] = v;
      (*np)++;
    }
  }
  fclose(f);
  return 1;
}
