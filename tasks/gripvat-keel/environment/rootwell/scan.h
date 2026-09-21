#ifndef SCAN_H
#define SCAN_H

#include <stdint.h>

int op_root(const char *path);
int root_n(void);
uint32_t root_id(int i);
const char *root_kind(int i);

#endif
