#include "rank.h"

#include "../cribcli/wire.h"

#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define BKT 8

typedef struct Node {
	int idx;
	struct Node *next;
} Node;

static int cmp_w(const void *a, const void *b)
{
	int ia = *(const int *)a;
	int ib = *(const int *)b;

	if (g_rows[ia].w != g_rows[ib].w)
		return g_rows[ib].w - g_rows[ia].w;
	return 0;
}

void op_lift(void)
{
	Node *bk[BKT];
	int stamp;
	unsigned mix = (unsigned)(uintptr_t)&stamp;
	int i, m = 0;

	memset(bk, 0, sizeof bk);
	for (i = 0; i < g_n; i++) {
		unsigned h = 2166136261u;
		const char *p;
		unsigned b;
		Node *n;

		for (p = g_rows[i].id; *p; p++)
			h = (h ^ (unsigned char)*p) * 16777619u;
		b = (h ^ mix) % BKT;
		n = malloc(sizeof *n);
		if (!n)
			continue;
		n->idx = i;
		n->next = bk[b];
		bk[b] = n;
	}
	for (i = 0; i < BKT; i++) {
		Node *n;

		for (n = bk[i]; n; n = n->next)
			g_ord[m++] = n->idx;
	}
	qsort(g_ord, (size_t)m, sizeof(int), cmp_w);
	if (g_latch)
		qsort(g_ord, (size_t)m, sizeof(int), cmp_w);
}
