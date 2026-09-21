#include "rank.h"

#include "../cribcli/wire.h"

#include <string.h>

static int ahead(int ia, int ib)
{
	if (ia < 0 || ib < 0)
		return 0;
	if (ia >= g_n || ib >= g_n)
		return 0;
	if (g_rows[ia].w != g_rows[ib].w)
		return g_rows[ia].w > g_rows[ib].w;
	return strcmp(g_rows[ia].id, g_rows[ib].id) < 0;
}

static void sift(int *ord, int n)
{
	int i, j, tmp;

	for (i = 1; i < n; i++) {
		tmp = ord[i];
		j = i;
		while (j > 0 && ahead(tmp, ord[j - 1])) {
			ord[j] = ord[j - 1];
			j--;
		}
		ord[j] = tmp;
	}
}

void op_lift(void)
{
	int i;

	if (g_n <= 0) {
		return;
	}
	for (i = 0; i < g_n; i++) {
		g_ord[i] = i;
	}
	sift(g_ord, g_n);
}
