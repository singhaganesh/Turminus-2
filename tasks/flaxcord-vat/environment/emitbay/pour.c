#include "pour.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

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

int n_pour(const char *a)
{
	FILE *fp;
	struct timespec ts;
	uint64_t stamp;
	int i, j;
	uint32_t ns, nlab;

	if (!a)
		return -1;
	bag_reset();
	for (i = 0; i < walk_n(); i++) {
		struct samp *s = walk_at(i);
		if (!s)
			continue;
		for (j = 0; j < s->depth; j++)
			op_bag(s->fr[j]);
	}
	bag_freeze();
	clock_gettime(CLOCK_REALTIME, &ts);
	stamp = (uint64_t)ts.tv_sec * 1000000ull + (uint64_t)(ts.tv_nsec / 1000);
	fp = fopen(a, "wb");
	if (!fp)
		return -1;
	fwrite(MAGIC, 1, 4, fp);
	wr64(fp, stamp);
	ns = bag_n();
	wr32(fp, ns);
	for (i = 0; i < (int)ns; i++) {
		const char *nm = bag_get((uint32_t)i);
		uint16_t ln = (uint16_t)strlen(nm ? nm : "");
		wr16(fp, ln);
		fwrite(nm ? nm : "", 1, ln, fp);
	}
	wr32(fp, (uint32_t)walk_n());
	for (i = 0; i < walk_n(); i++) {
		struct samp *s = walk_at(i);
		wr16(fp, (uint16_t)s->depth);
		for (j = 0; j < s->depth; j++)
			wr32(fp, op_bag(s->fr[j]));
		wr32(fp, s->hits);
	}
	nlab = (uint32_t)walk_n();
	wr32(fp, nlab);
	for (i = 0; i < walk_n(); i++) {
		struct samp *s = walk_at(i);
		uint16_t ln = (uint16_t)strlen(s->lab);
		wr16(fp, ln);
		fwrite(s->lab, 1, ln, fp);
	}
	fclose(fp);
	return 0;
}
