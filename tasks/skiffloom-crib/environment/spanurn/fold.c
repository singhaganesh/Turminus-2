#include "fold.h"

#include "../cribcli/wire.h"

#include <string.h>

static int has_line(const int *lines, int n, int v)
{
	int i;

	for (i = 0; i < n; i++) {
		if (lines[i] == v)
			return 1;
	}
	return 0;
}

int cfg_span(void)
{
	int i, f, h, ln;

	for (i = 0; i < g_n; i++)
		g_rows[i].w = 0;
	for (f = 0; f < g_nchgf; f++) {
		for (i = 0; i < g_n; i++) {
			int w = 0;
			Sheet *sh = &g_sheets[i];

			for (h = 0; h < sh->nfiles; h++) {
				if (strcmp(sh->files[h].path, g_chgf[f].path) != 0)
					continue;
				for (ln = 0; ln < g_chgf[f].nlines; ln++) {
					if (has_line(sh->files[h].lines, sh->files[h].nlines,
						     g_chgf[f].lines[ln]))
						w++;
				}
			}
			g_rows[i].w = w;
		}
	}
	{
		int k = 0;

		for (i = 0; i < g_n; i++) {
			if (g_rows[i].w <= 0)
				continue;
			if (k != i) {
				g_rows[k] = g_rows[i];
				g_sheets[k] = g_sheets[i];
			}
			k++;
		}
		g_n = k;
	}
	return 0;
}
