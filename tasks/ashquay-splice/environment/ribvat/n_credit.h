#ifndef N_CREDIT_H
#define N_CREDIT_H

typedef struct Sel {
  char bid[32];
  char host[64];
} Sel;

int n_credit(const char *a, const struct Sel *b, int c);

#endif
