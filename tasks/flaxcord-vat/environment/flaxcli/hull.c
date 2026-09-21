#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#include "serial.h"
#include "../cordspin/bag.h"
#include "../chunkvat/walk.h"
#include "../emitbay/pour.h"
#include "../differbay/cmp.h"
#include "../unreelkit/show.h"

static void mark_ok(void)
{
	FILE *fp;

	mkdir("/app/cordwell", 0755);
	fp = fopen("/app/cordwell/spin.ok", "w");
	if (fp) {
		fputs("ok\n", fp);
		fclose(fp);
	}
}

static void clear_ok(void)
{
	unlink("/app/cordwell/spin.ok");
}

int main(int argc, char **argv)
{
	take_join(argc, argv);
	if (argc < 2) {
		fputs("usage\n", stderr);
		return 2;
	}
	if (strcmp(argv[1], "spin") == 0) {
		const char *dir;
		const char *outp;

		if (argc < 4)
			return 2;
		dir = argv[2];
		outp = argv[3];
		mkdir("/app/cordwell", 0755);
		clear_ok();
		bag_reset();
		if (cfg_walk(dir) != 0)
			return 1;
		if (n_pour(outp) != 0)
			return 1;
		mark_ok();
		return 0;
	}
	if (strcmp(argv[1], "unreel") == 0) {
		if (argc < 3)
			return 2;
		return run_show(argv[2]);
	}
	if (strcmp(argv[1], "differ") == 0) {
		if (argc < 4)
			return 2;
		mkdir("/app/cordwell", 0755);
		return run_cmp(argv[2], argv[3], "/app/cordwell/differ.txt");
	}
	return 2;
}
