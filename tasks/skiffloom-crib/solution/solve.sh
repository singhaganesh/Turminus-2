#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd /app
cat > /app/heapwell/rank.c << 'ENDRANK'
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
ENDRANK
cat > /app/spanurn/fold.c << 'ENDFOLD'
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
ENDFOLD
cat > /app/tickpit/trim.c << 'ENDTRIM'
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
ENDTRIM
rm -f /app/heapwell/*.rej /app/spanurn/*.rej /app/tickpit/*.rej
chmod +x /app/kindle.sh
/app/kindle.sh
mkdir -p /app/slatewell /app/slatewell/mornbox
/app/bin/skiffloom cull /app/deltabay/eve.chg /app/slatewell
/app/bin/skiffloom cull /app/deltabay/morn.chg /app/slatewell/mornbox
