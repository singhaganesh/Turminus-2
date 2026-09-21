#include "latch.h"

#include <string.h>

int g_latch;

void take_latch(int argc, char **argv)
{
	int i;

	g_latch = 0;
	for (i = 1; i < argc; i++) {
		if (strcmp(argv[i], "--pin-handles") == 0)
			g_latch = 1;
	}
}
