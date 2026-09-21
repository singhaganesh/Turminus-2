#include "scan.h"

#include "../millarm/load.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_R 32

typedef struct {
	uint32_t id;
	char kind[MAX_S];
} RootRec;

static RootRec *rptr[MAX_R];
static RootRec rbuf[MAX_R];
static int nr;

static int kind_rank(const char *k)
{
	if (strcmp(k, "JNI") == 0)
		return 0;
	if (strcmp(k, "STACK") == 0)
		return 1;
	if (strcmp(k, "VM") == 0)
		return 2;
	return 8;
}

static int cmp_kind(const void *a, const void *b)
{
	const RootRec *ra = *(RootRec * const *)a;
	const RootRec *rb = *(RootRec * const *)b;
	int ka = kind_rank(ra->kind);
	int kb = kind_rank(rb->kind);
	int c;
	const char *ca;
	const char *cb;

	if (ka != kb)
		return ka - kb;
	c = strcmp(ra->kind, rb->kind);
	if (c)
		return c;
	ca = node_cls(ra->id);
	cb = node_cls(rb->id);
	c = strcmp(ca, cb);
	if (c)
		return c;
	if (ra->id < rb->id)
		return -1;
	if (ra->id > rb->id)
		return 1;
	return 0;
}

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
		if (line[0] == '#' || line[0] == '\n')
			continue;
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
	if (!load_ended())
		return -1;
	if (nr <= 0)
		return -1;
	{
		int w = 0;
		int r;
		int s;
		int seen;

		for (r = 0; r < nr; r++) {
			seen = 0;
			for (s = 0; s < w; s++) {
				if (rptr[s]->id == rptr[r]->id)
					seen = 1;
			}
			if (!seen) {
				rptr[w] = rptr[r];
				w++;
			}
		}
		nr = w;
	}
	qsort(rptr, (size_t)nr, sizeof(rptr[0]), cmp_kind);
	return 0;
}
