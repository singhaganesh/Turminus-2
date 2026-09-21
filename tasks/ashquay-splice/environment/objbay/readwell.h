#ifndef READWELL_H
#define READWELL_H

typedef struct Obj {
  char host[64];
  char bid[32];
  char root[256];
  int rank;
  int n_sym;
  int n_line;
  unsigned addrs[64];
  char names[64][64];
  unsigned laddr[64];
  char lfile[64][80];
} Obj;

int load_cards(char hosts[][64], int ranks[], char roots[][256], int maxn);
int well_root(const char *host, char *root, int n);
int load_dbg(const char *path, const char *host, int rank, Obj *o);
int load_core(const char *path, char mods[][32], unsigned bases[], int *nm,
              unsigned pcs[], int *np);

#endif
