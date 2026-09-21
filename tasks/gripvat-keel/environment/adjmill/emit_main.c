#include "emit.h"

#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv)
{
	FILE *fp;

	if (argc < 2)
		return 2;
	fp = fopen(argv[1], "w");
	if (!fp)
		return 1;
	cfg_emit(fp);
	fclose(fp);
	return 0;
}
