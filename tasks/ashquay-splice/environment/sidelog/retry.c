#include "retry.h"

#include <stdio.h>

void retry_touch(char hosts[][64], int n) {
  FILE *f = fopen("/app/outkeg/poll.log", "w");
  int i;
  if (!f) {
    return;
  }
  for (i = 0; i < n; i++) {
    fprintf(f, "%s\n", hosts[i]);
  }
  fclose(f);
}
