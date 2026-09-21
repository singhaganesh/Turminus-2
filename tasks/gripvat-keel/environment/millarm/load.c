#include "load.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static Node nodes[MAX_N];
static Edge edges[MAX_E];
static uint32_t sites[MAX_N];
static int nn, ne, ns, ended;

void load_reset(void)
{
	nn = ne = ns = ended = 0;
}

int load_ended(void)
{
	return ended;
}

int node_n(void) { return nn; }
int edge_n(void) { return ne; }
int site_n(void) { return ns; }

const Node *node_at(int i) { return &nodes[i]; }
const Edge *edge_at(int i) { return &edges[i]; }
uint32_t site_at(int i) { return sites[i]; }

int node_index(uint32_t id)
{
	int i;

	for (i = 0; i < nn; i++) {
		if (nodes[i].id == id)
			return i;
	}
	return -1;
}

const char *node_cls(uint32_t id)
{
	int i = node_index(id);

	if (i < 0)
		return "";
	return nodes[i].cls;
}

uint32_t node_bytes(uint32_t id)
{
	int i = node_index(id);

	if (i < 0)
		return 0;
	return nodes[i].bytes;
}

int load_card(const char *path)
{
	FILE *fp;
	char line[256];
	char a[64], b[64], c[64];
	uint32_t x, y, z;

	load_reset();
	fp = fopen(path, "r");
	if (!fp)
		return -1;
	if (!fgets(line, sizeof(line), fp)) {
		fclose(fp);
		return -1;
	}
	if (strncmp(line, "HPK1", 4) != 0) {
		fclose(fp);
		return -1;
	}
	while (fgets(line, sizeof(line), fp)) {
		if (strncmp(line, "END", 3) == 0) {
			ended = 1;
			break;
		}
		if (sscanf(line, "NODE %u %31s %u", &x, a, &z) == 3) {
			if (nn >= MAX_N) {
				fclose(fp);
				return -1;
			}
			nodes[nn].id = x;
			strncpy(nodes[nn].cls, a, MAX_S - 1);
			nodes[nn].cls[MAX_S - 1] = 0;
			nodes[nn].bytes = z;
			nn++;
			continue;
		}
		if (sscanf(line, "EDGE %u %u %31s %31s", &x, &y, b, c) == 4) {
			if (ne >= MAX_E) {
				fclose(fp);
				return -1;
			}
			edges[ne].from = x;
			edges[ne].to = y;
			edges[ne].kind = (strcmp(b, "STRONG") == 0) ? KIND_STRONG : KIND_WEAK;
			strncpy(edges[ne].field, c, MAX_S - 1);
			edges[ne].field[MAX_S - 1] = 0;
			ne++;
			continue;
		}
		if (sscanf(line, "ROOT %u %31s", &x, a) == 2) {
			(void)a;
			continue;
		}
		if (sscanf(line, "SITE %u", &x) == 1) {
			if (ns >= MAX_N) {
				fclose(fp);
				return -1;
			}
			sites[ns++] = x;
			continue;
		}
	}
	fclose(fp);
	return 0;
}
