#include "pour.h"

#include "../cribcli/wire.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>

static void wr16(FILE *fp, uint16_t v)
{
	unsigned char b[2];

	b[0] = (unsigned char)((v >> 8) & 0xff);
	b[1] = (unsigned char)(v & 0xff);
	fwrite(b, 1, 2, fp);
}

static void wr32(FILE *fp, uint32_t v)
{
	unsigned char b[4];

	b[0] = (unsigned char)((v >> 24) & 0xff);
	b[1] = (unsigned char)((v >> 16) & 0xff);
	b[2] = (unsigned char)((v >> 8) & 0xff);
	b[3] = (unsigned char)(v & 0xff);
	fwrite(b, 1, 4, fp);
}

static void wr_ids(FILE *fp, const int *idx, int n)
{
	int i;

	wr16(fp, (uint16_t)n);
	for (i = 0; i < n; i++) {
		const char *id = g_rows[idx[i]].id;
		uint16_t ln = (uint16_t)strlen(id);

		wr16(fp, ln);
		fwrite(id, 1, ln, fp);
	}
}

int n_pour(const char *dest)
{
	char jpath[256], bpath[256];
	FILE *jp, *bp;
	int i;

	mkdir(dest, 0755);
	snprintf(jpath, sizeof jpath, "%s/slate.json", dest);
	snprintf(bpath, sizeof bpath, "%s/slate.bin", dest);
	jp = fopen(jpath, "w");
	bp = fopen(bpath, "wb");
	if (!jp || !bp) {
		if (jp)
			fclose(jp);
		if (bp)
			fclose(bp);
		return 1;
	}
	fputs("{\"pool\":[", jp);
	for (i = 0; i < g_n; i++) {
		if (i)
			fputc(',', jp);
		fprintf(jp, "\"%s\"", g_rows[g_ord[i]].id);
	}
	fputs("],\"names\":[", jp);
	for (i = 0; i < g_sel_n; i++) {
		if (i)
			fputc(',', jp);
		fprintf(jp, "\"%s\"", g_rows[g_sel[i]].id);
	}
	fprintf(jp, "],\"spent_ms\":%d}\n", g_spent);
	fclose(jp);
	fwrite("SLT1", 1, 4, bp);
	wr_ids(bp, g_ord, g_n);
	wr_ids(bp, g_sel, g_sel_n);
	wr32(bp, (uint32_t)g_spent);
	fclose(bp);
	return 0;
}
