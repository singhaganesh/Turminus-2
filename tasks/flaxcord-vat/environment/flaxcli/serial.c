#include "serial.h"

#include <string.h>

int g_join;

void take_join(int argc, char **argv)
{
	int i;

	g_join = 0;
	for (i = 1; i < argc; i++) {
		if (strcmp(argv[i], "--serial-decode") == 0)
			g_join = 1;
	}
}
