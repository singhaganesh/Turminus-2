#ifndef BAG_H
#define BAG_H

#include <stdint.h>

void bag_reset(void);
uint32_t op_bag(const char *a);
void bag_freeze(void);
const char *bag_get(uint32_t id);
uint32_t bag_n(void);

#endif
