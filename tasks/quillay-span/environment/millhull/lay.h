#ifndef LAY_H
#define LAY_H

struct Lay {
  char path[256];
  unsigned long long dev;
  unsigned long long ino;
  char dig[65];
  unsigned long long vma;
  unsigned long long off;
  unsigned long long sz;
};

#endif
