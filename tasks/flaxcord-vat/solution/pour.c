#include "pour.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../cordspin/bag.h"
#include "../chunkvat/walk.h"
#include "../flaxcli/wire.h"

static void wr16(FILE *fp, uint16_t v)
{
	unsigned char b[2];

	b[0] = (unsigned char)(v & 0xff);
	b[1] = (unsigned char)((v >> 8) & 0xff);
	fwrite(b, 1, 2, fp);
}

static void wr32(FILE *fp, uint32_t v)
{
	unsigned char b[4];

	b[0] = (unsigned char)(v & 0xff);
	b[1] = (unsigned char)((v >> 8) & 0xff);
	b[2] = (unsigned char)((v >> 16) & 0xff);
	b[3] = (unsigned char)((v >> 24) & 0xff);
	fwrite(b, 1, 4, fp);
}

static void wr64(FILE *fp, uint64_t v)
{
	unsigned char b[8];
	int i;

	for (i = 0; i < 8; i++)
		b[i] = (unsigned char)((v >> (8 * i)) & 0xff);
	fwrite(b, 1, 8, fp);
}

static void join_path(const struct samp *s, char *out, int cap)
{
	int j;

	out[0] = 0;
	for (j = 0; j < s->depth; j++) {
		if (j)
			strncat(out, ">", (size_t)cap - 1);
		strncat(out, s->fr[j], (size_t)cap - 1);
	}
}

static int cmp_path(const void *x, const void *y)
{
	char pa[512], pb[512];
	const struct samp *a = x;
	const struct samp *b = y;
	int c;

	join_path(a, pa, 512);
	join_path(b, pb, 512);
	c = strcmp(pa, pb);
	if (c)
		return c;
	if (a->seq < b->seq)
		return -1;
	if (a->seq > b->seq)
		return 1;
	return 0;
}

static int cmp_lab_seq(const void *x, const void *y)
{
	const struct samp *a = x;
	const struct samp *b = y;

	if (a->seq < b->seq)
		return -1;
	if (a->seq > b->seq)
		return 1;
	return strcmp(a->lab, b->lab);
}

int n_pour(const char *a)
{
	FILE *fp;
	int i, j;
	uint32_t ns;
	struct samp *copy;
	int n;

	if (!a)
		return -1;
	n = walk_n();
	copy = calloc((size_t)n + 1, sizeof(*copy));
	if (!copy)
		return -1;
	for (i = 0; i < n; i++)
		copy[i] = *walk_at(i);
	bag_reset();
	for (i = 0; i < n; i++) {
		for (j = 0; j < copy[i].depth; j++)
			op_bag(copy[i].fr[j]);
	}
	bag_freeze();
	qsort(copy, (size_t)n, sizeof(*copy), cmp_path);
	fp = fopen(a, "wb");
	if (!fp) {
		free(copy);
		return -1;
	}
	fwrite(MAGIC, 1, 4, fp);
	wr64(fp, 0);
	ns = bag_n();
	wr32(fp, ns);
	for (i = 0; i < (int)ns; i++) {
		const char *nm = bag_get((uint32_t)i);
		uint16_t ln = (uint16_t)strlen(nm ? nm : "");
		wr16(fp, ln);
		fwrite(nm ? nm : "", 1, ln, fp);
	}
	wr32(fp, (uint32_t)n);
	for (i = 0; i < n; i++) {
		wr16(fp, (uint16_t)copy[i].depth);
		for (j = 0; j < copy[i].depth; j++)
			wr32(fp, op_bag(copy[i].fr[j]));
		wr32(fp, copy[i].hits);
	}
	qsort(copy, (size_t)n, sizeof(*copy), cmp_lab_seq);
	wr32(fp, (uint32_t)n);
	for (i = 0; i < n; i++) {
		uint16_t ln = (uint16_t)strlen(copy[i].lab);
		wr16(fp, ln);
		fwrite(copy[i].lab, 1, ln, fp);
	}
	fclose(fp);
	free(copy);
	return 0;
}
