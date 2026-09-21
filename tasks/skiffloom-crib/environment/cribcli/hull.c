#include "latch.h"
#include "load.h"
#include "flow.h"
#include "../spanurn/fold.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

static void mark_ok(void)
{
	FILE *fp;

	mkdir("/app/slatewell", 0755);
	fp = fopen("/app/slatewell/cull.ok", "w");
	if (fp) {
		fputs("ok\n", fp);
		fclose(fp);
	}
}

static void clear_ok(void)
{
	unlink("/app/slatewell/cull.ok");
}

int main(int argc, char **argv)
{
	const char *card;
	const char *dest;

	take_latch(argc, argv);
	if (argc < 2) {
		fputs("usage\n", stderr);
		return 2;
	}
	if (strcmp(argv[1], "cull") != 0)
		return 2;
	if (argc < 4)
		return 2;
	card = argv[2];
	dest = argv[3];
	mkdir("/app/slatewell", 0755);
	clear_ok();
	if (load_card(card) != 0)
		return 1;
	if (cfg_span() != 0)
		return 1;
	if (run_flow(dest) != 0)
		return 1;
	mark_ok();
	return 0;
}
