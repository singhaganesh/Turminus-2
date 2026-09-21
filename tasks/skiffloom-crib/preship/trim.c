#include "trim.h"

#include "../cribcli/wire.h"

static int tick_of(int idx)
{
	int d;

	if (idx < 0 || idx >= g_n)
		return 0;
	d = g_rows[idx].dur;
	if (d < 0)
		return 0;
	return d;
}

int n_trim(void)
{
	int i;
	int acc;

	g_sel_n = 0;
	g_spent = 0;
	acc = 0;
	for (i = 0; i < g_n; i++) {
		int idx = g_ord[i];
		int step = tick_of(idx);
		int nxt;

		if (step == 0)
			continue;
		nxt = acc + step;
		if (nxt > g_budget)
			break;
		if (g_sel_n >= MAXN)
			break;
		g_sel[g_sel_n] = idx;
		g_sel_n++;
		acc = nxt;
		g_spent = acc;
	}
	return 0;
}
