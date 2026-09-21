#include "step.h"

#include "../millarm/load.h"
#include "../millarm/latch.h"
#include "../rootwell/scan.h"
#include "../softbay/skip.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#define INF 1000000

#include "step.inc"

static Edge *nb[MAX_E];

static int collect_nb(uint32_t from)
{
	int i, n = 0;

	for (i = 0; i < edge_n(); i++) {
		const Edge *e = edge_at(i);

		if (e->from != from)
			continue;
		if (!n_soft(e->kind))
			continue;
		nb[n++] = (Edge *)e;
	}
	if (g_latch) {
		/* pin flag is accepted; comparator still comes from step.inc */
		(void)g_latch;
	}
	qsort(nb, (size_t)n, sizeof(nb[0]), nbor_ord);
	return n;
}

static void emit_path(FILE *fp, int *pred_e, int site_idx, const char *rk)
{
	int chain[MAX_N];
	int n = 0;
	int cur = site_idx;
	int i;

	while (cur >= 0 && n < MAX_N) {
		chain[n++] = cur;
		if (pred_e[cur] < 0)
			break;
		cur = node_index(edge_at(pred_e[cur])->from);
	}
	fprintf(fp, "PATH %s", rk);
	for (i = n - 2; i >= 0; i--) {
		const Edge *e = edge_at(pred_e[chain[i]]);

		fprintf(fp, ">%s.%s", node_cls(e->to), e->field);
	}
	fputc('\n', fp);
}

int run_step(const char *card, const char *ledger)
{
	int dist[MAX_N];
	int pred_e[MAX_N];
	int q[MAX_N];
	int qh, qt, i, r, s, si, found;
	FILE *fp;
	const char *use_rk = "";
	int use_site = -1;

	(void)card;
	for (i = 0; i < node_n(); i++) {
		dist[i] = INF;
		pred_e[i] = -1;
	}
	found = 0;
	for (r = 0; r < root_n() && !found; r++) {
		int ri = node_index(root_id(r));

		if (ri < 0)
			continue;
		for (i = 0; i < node_n(); i++) {
			dist[i] = INF;
			pred_e[i] = -1;
		}
		qh = qt = 0;
		dist[ri] = 0;
		q[qt++] = ri;
		while (qh < qt) {
			int u = q[qh++];
			int nn = collect_nb(node_at(u)->id);
			int k;

			for (k = 0; k < nn; k++) {
				int v = node_index(nb[k]->to);
				int nd;

				if (v < 0)
					continue;
				nd = dist[u] + 1;
				if (nd < dist[v]) {
					dist[v] = nd;
					pred_e[v] = (int)(nb[k] - edge_at(0));
					q[qt++] = v;
				}
			}
		}
		for (s = 0; s < site_n(); s++) {
			si = node_index(site_at(s));
			if (si >= 0 && dist[si] < INF) {
				found = 1;
				use_rk = root_kind(r);
				use_site = si;
				break;
			}
		}
	}
	fp = fopen(ledger, "w");
	if (!fp)
		return -1;
	if (!found) {
		fclose(fp);
		return -1;
	}
	fprintf(fp, "SITE %s\n", node_cls(node_at(use_site)->id));
	fprintf(fp, "BYTES %u\n", node_bytes(node_at(use_site)->id));
	emit_path(fp, pred_e, use_site, use_rk);
	fclose(fp);
	return 0;
}
