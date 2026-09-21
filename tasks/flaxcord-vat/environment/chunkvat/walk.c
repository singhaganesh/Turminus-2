#include "walk.h"

#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../flaxcli/serial.h"

#define NB 16

struct ent {
	char path[512];
	struct ent *next;
};

static struct samp tab[MAX_CH];
static int ntab;
static struct ent *buck[NB];

static unsigned hname(const char *s)
{
	unsigned h = 2166136261u;

	while (*s)
		h = (h ^ (unsigned char)*s++) * 16777619u;
	return h % NB;
}

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
	(void)got_end;
	return 0;
}

int cfg_walk(const char *a)
{
	DIR *d;
	struct dirent *de;
	int i;

	ntab = 0;
	for (i = 0; i < NB; i++)
		buck[i] = NULL;
	(void)g_join;
	d = opendir(a ? a : ".");
	if (!d)
		return -1;
	while ((de = readdir(d)) != NULL) {
		struct ent *e;
		unsigned h;

		if (de->d_name[0] == '.')
			continue;
		if (!strstr(de->d_name, ".chk"))
			continue;
		h = hname(de->d_name);
		e = calloc(1, sizeof(*e));
		if (!e)
			continue;
		snprintf(e->path, sizeof(e->path), "%s/%s", a, de->d_name);
		e->next = buck[h];
		buck[h] = e;
	}
	closedir(d);
	for (i = 0; i < NB; i++) {
		struct ent *e = buck[i];
		while (e) {
			struct ent *n = e->next;
			if (ntab < MAX_CH) {
				if (parse_one(e->path, &tab[ntab]) == 0) {
					const char *slash = strrchr(e->path, '/');
					strncpy(tab[ntab].lab, slash ? slash + 1 : e->path, MAX_LN - 1);
					ntab++;
				}
			}
			free(e);
			e = n;
		}
		buck[i] = NULL;
	}
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
