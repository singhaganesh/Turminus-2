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

static int sheet_hits_pair(const Sheet *sh, const char *path, int ln)
{
	int h;

	for (h = 0; h < sh->nfiles; h++) {
		if (strcmp(sh->files[h].path, path) != 0)
			continue;
		if (has_line(sh->files[h].lines, sh->files[h].nlines, ln))
			return 1;
	}
	return 0;
}

static int count_union(int idx)
{
	int f, ln, w = 0;
	Sheet *sh = &g_sheets[idx];

	for (f = 0; f < g_nchgf; f++) {
		for (ln = 0; ln < g_chgf[f].nlines; ln++) {
			if (sheet_hits_pair(sh, g_chgf[f].path, g_chgf[f].lines[ln]))
				w++;
		}
	}
	return w;
}

static void drop_zero(void)
{
	int i, k = 0;

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

int cfg_span(void)
{
	int i;

	if (strcmp(g_origin, "voided") == 0)
		return -1;
	for (i = 0; i < g_n; i++)
		g_rows[i].w = 0;
	for (i = 0; i < g_n; i++)
		g_rows[i].w = count_union(i);
	drop_zero();
	return 0;
}
