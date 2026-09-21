#include "show.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint16_t rd16(FILE *fp)
{
	unsigned char b[2];

	if (fread(b, 1, 2, fp) != 2)
		return 0;
	return (uint16_t)(b[0] | ((uint16_t)b[1] << 8));
}

static uint32_t rd32(FILE *fp)
{
	unsigned char b[4];

	if (fread(b, 1, 4, fp) != 4)
		return 0;
	return (uint32_t)b[0] | ((uint32_t)b[1] << 8) | ((uint32_t)b[2] << 16) |
	       ((uint32_t)b[3] << 24);
}

static uint64_t rd64(FILE *fp)
{
	unsigned char b[8];
	uint64_t v = 0;
	int i;

	if (fread(b, 1, 8, fp) != 8)
		return 0;
	for (i = 0; i < 8; i++)
		v |= (uint64_t)b[i] << (8 * i);
	return v;
}

int run_show(const char *a)
{
	FILE *fp;
	char mag[4];
	uint32_t nstr, nsamp, i, j;
	char **tab;

	fp = fopen(a, "rb");
	if (!fp)
		return 1;
	if (fread(mag, 1, 4, fp) != 4) {
		fclose(fp);
		return 1;
	}
	(void)rd64(fp);
	nstr = rd32(fp);
	tab = calloc(nstr + 1, sizeof(char *));
	for (i = 0; i < nstr; i++) {
		uint16_t ln = rd16(fp);
		tab[i] = calloc(ln + 1, 1);
		if (ln)
			fread(tab[i], 1, ln, fp);
	}
	nsamp = rd32(fp);
	for (i = 0; i < nsamp; i++) {
		uint16_t depth = rd16(fp);
		for (j = 0; j < depth; j++) {
			uint32_t id = rd32(fp);
			if (j)
				fputc('>', stdout);
			if (id < nstr && tab[id])
				fputs(tab[id], stdout);
		}
		printf(" COUNT %u\n", rd32(fp));
	}
	for (i = 0; i < nstr; i++)
		free(tab[i]);
	free(tab);
	fclose(fp);
	return 0;
}
