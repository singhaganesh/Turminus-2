#include "trim.h"

#include "../cribcli/wire.h"

int n_trim(void)
{
	int i, cap = 4;

	g_sel_n = 0;
	g_spent = 0;
	if (cap > g_n)
		cap = g_n;
	for (i = 0; i < cap; i++) {
		int idx = g_ord[i];

		g_sel[g_sel_n++] = idx;
		g_spent += g_rows[idx].dur;
	}
	return 0;
}
