#include "cmp.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int run_cmp(const char *a, const char *b, const char *outp)
{
	FILE *fa, *fb, *fo;
	unsigned char *x = NULL, *y = NULL;
	long na, nb;
	int same = 0;

	fa = fopen(a, "rb");
	fb = fopen(b, "rb");
	if (!fa || !fb) {
		if (fa)
			fclose(fa);
		if (fb)
			fclose(fb);
		fo = fopen(outp, "w");
		if (fo) {
			fputs("noisy\n", fo);
			fclose(fo);
		}
		return 1;
	}
	fseek(fa, 0, SEEK_END);
	na = ftell(fa);
	fseek(fa, 0, SEEK_SET);
	fseek(fb, 0, SEEK_END);
	nb = ftell(fb);
	fseek(fb, 0, SEEK_SET);
	if (na == nb && na >= 0) {
		x = malloc((size_t)na);
		y = malloc((size_t)nb);
		if (x && y && fread(x, 1, (size_t)na, fa) == (size_t)na &&
		    fread(y, 1, (size_t)nb, fb) == (size_t)nb)
			same = memcmp(x, y, (size_t)na) == 0;
	}
	free(x);
	free(y);
	fclose(fa);
	fclose(fb);
	fo = fopen(outp, "w");
	if (!fo)
		return 1;
	fputs(same ? "quiet\n" : "noisy\n", fo);
	fclose(fo);
	return same ? 0 : 1;
}
