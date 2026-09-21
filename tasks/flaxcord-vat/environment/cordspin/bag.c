#include "bag.h"

#include <string.h>

#define MAX_PLACE 256

static char names[MAX_PLACE][80];
static uint32_t ids[MAX_PLACE];
static uint32_t ntab;

void bag_reset(void)
{
	ntab = 0;
}

uint32_t op_bag(const char *a)
{
	uint32_t i;

	if (!a)
		a = "";
	for (i = 0; i < ntab; i++) {
		if (strcmp(names[i], a) == 0)
			return ids[i];
	}
	if (ntab >= MAX_PLACE)
		return 0;
	strncpy(names[ntab], a, 79);
	names[ntab][79] = 0;
	ids[ntab] = ntab;
	ntab++;
	return ids[ntab - 1];
}

void bag_freeze(void)
{
}

const char *bag_get(uint32_t id)
{
	uint32_t i;

	for (i = 0; i < ntab; i++) {
		if (ids[i] == id)
			return names[i];
	}
	return "";
}

uint32_t bag_n(void)
{
	return ntab;
}
