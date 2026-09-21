#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#include "latch.h"
#include "load.h"
#include "../rootwell/scan.h"
#include "../ridget/step.h"
#include "../twinline/note.h"

static void mark_ok(void)
{
	FILE *fp;

	mkdir("/app/inkurn", 0755);
	fp = fopen("/app/inkurn/mint.ok", "w");
	if (fp) {
		fputs("ok\n", fp);
		fclose(fp);
	}
}

static void clear_ok(void)
{
	unlink("/app/inkurn/mint.ok");
}

int main(int argc, char **argv)
{
	take_latch(argc, argv);
	if (argc < 2) {
		fputs("usage\n", stderr);
		return 2;
	}
	if (strcmp(argv[1], "mint") == 0) {
		const char *card;
		const char *outp;

		if (argc < 4)
			return 2;
		card = argv[2];
		outp = argv[3];
		mkdir("/app/inkurn", 0755);
		clear_ok();
		if (load_card(card) != 0)
			return 1;
		if (op_root(card) != 0)
			return 1;
		if (run_step(card, outp) != 0)
			return 1;
		mark_ok();
		return 0;
	}
	if (strcmp(argv[1], "align") == 0) {
		if (argc < 4)
			return 2;
		mkdir("/app/inkurn", 0755);
		return run_note(argv[2], argv[3], "/app/inkurn/align.txt") == 0 ? 0 : 1;
	}
	return 2;
}
