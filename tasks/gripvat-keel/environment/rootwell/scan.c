#include "scan.h"

#include "../millarm/load.h"

#include <stdio.h>
#include <string.h>

#define MAX_R 32

typedef struct {
	uint32_t id;
	char kind[MAX_S];
} RootRec;

static RootRec *rptr[MAX_R];
static RootRec rbuf[MAX_R];
static int nr;

int root_n(void)
{
	return nr;
}

uint32_t root_id(int i)
{
	return rptr[i]->id;
}

const char *root_kind(int i)
{
	return rptr[i]->kind;
}

int op_root(const char *path)
{
	FILE *fp;
	char line[256];
	char k[MAX_S];
	uint32_t id;

	nr = 0;
	fp = fopen(path, "r");
	if (!fp)
		return -1;
	while (fgets(line, sizeof(line), fp)) {
		if (sscanf(line, "ROOT %u %31s", &id, k) == 2) {
			if (nr >= MAX_R) {
				fclose(fp);
				return -1;
			}
			rbuf[nr].id = id;
			strncpy(rbuf[nr].kind, k, MAX_S - 1);
			rbuf[nr].kind[MAX_S - 1] = 0;
			rptr[nr] = &rbuf[nr];
			nr++;
		}
	}
	fclose(fp);
	return 0;
}
