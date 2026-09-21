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
	char tmp[MAX_PLACE][80];
	uint32_t i, j, n = ntab, m = 0;

	if (n == 0)
		return;
	for (i = 0; i < n; i++)
		memcpy(tmp[i], names[i], 80);
	for (i = 1; i < n; i++) {
		char row[80];
		memcpy(row, tmp[i], 80);
		j = i;
		while (j > 0 && strcmp(tmp[j - 1], row) > 0) {
			memcpy(tmp[j], tmp[j - 1], 80);
			j--;
		}
		memcpy(tmp[j], row, 80);
	}
	for (i = 0; i < n; i++) {
		if (tmp[i][0] == 0)
			continue;
		if (m && strcmp(tmp[i], tmp[m - 1]) == 0)
			continue;
		if (m != i)
			memcpy(tmp[m], tmp[i], 80);
		m++;
	}
	ntab = 0;
	for (i = 0; i < m; i++) {
		strncpy(names[i], tmp[i], 79);
		names[i][79] = 0;
		ids[i] = i;
		ntab++;
	}
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
