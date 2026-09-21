#include "note.h"

#include <stdio.h>
#include <string.h>

int run_note(const char *left, const char *right, const char *outp)
{
	FILE *a, *b, *o;
	char la[512], lb[512];
	int ok = 1;

	a = fopen(left, "r");
	b = fopen(right, "r");
	o = fopen(outp, "w");
	if (!a || !b || !o) {
		if (a)
			fclose(a);
		if (b)
			fclose(b);
		if (o)
			fclose(o);
		return -1;
	}
	while (1) {
		char *ga = fgets(la, sizeof(la), a);
		char *gb = fgets(lb, sizeof(lb), b);

		if (!ga && !gb)
			break;
		if (!ga || !gb || strcmp(la, lb) != 0) {
			ok = 0;
			break;
		}
	}
	fputs(ok ? "lock\n" : "slip\n", o);
	fclose(a);
	fclose(b);
	fclose(o);
	return 0;
}
