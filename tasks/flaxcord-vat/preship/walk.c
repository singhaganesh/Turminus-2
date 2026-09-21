#include "walk.h"

#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../flaxcli/serial.h"

static struct samp tab[MAX_CH];
static int ntab;

static int parse_one(const char *path, struct samp *out)
{
	FILE *fp;
	char line[128];
	int got_end = 0;

	memset(out, 0, sizeof(*out));
	fp = fopen(path, "r");
	if (!fp)
		return -1;
	while (fgets(line, sizeof(line), fp)) {
		char *nl = strchr(line, '\n');
		if (nl)
			*nl = 0;
		if (strncmp(line, "SEQ ", 4) == 0)
			out->seq = (uint32_t)atoi(line + 4);
		else if (strncmp(line, "HITS ", 5) == 0)
			out->hits = (uint32_t)atoi(line + 5);
		else if (strcmp(line, "END") == 0)
			got_end = 1;
		else if (line[0] && out->depth < MAX_FR) {
			strncpy(out->fr[out->depth], line, MAX_LN - 1);
			out->depth++;
		}
	}
	fclose(fp);
	if (!got_end)
		return -1;
	return 0;
}

static int cmp_seq(const void *x, const void *y)
{
	const struct samp *a = x;
	const struct samp *b = y;

	if (a->seq < b->seq)
		return -1;
	if (a->seq > b->seq)
		return 1;
	return strcmp(a->lab, b->lab);
}

int cfg_walk(const char *a)
{
	DIR *d;
	struct dirent *de;
	char full[512];

	(void)g_join;
	ntab = 0;
	d = opendir(a ? a : ".");
	if (!d)
		return -1;
	while ((de = readdir(d)) != NULL) {
		if (de->d_name[0] == '.')
			continue;
		if (!strstr(de->d_name, ".chk"))
			continue;
		snprintf(full, sizeof(full), "%s/%s", a, de->d_name);
		if (ntab >= MAX_CH) {
			closedir(d);
			return -1;
		}
		if (parse_one(full, &tab[ntab]) != 0) {
			closedir(d);
			return -1;
		}
		snprintf(tab[ntab].lab, MAX_LN, "%u", tab[ntab].seq);
		ntab++;
	}
	closedir(d);
	qsort(tab, (size_t)ntab, sizeof(tab[0]), cmp_seq);
	return 0;
}

int walk_n(void)
{
	return ntab;
}

struct samp *walk_at(int i)
{
	if (i < 0 || i >= ntab)
		return NULL;
	return &tab[i];
}
