#include "load.h"

#include "wire.h"

#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

Row g_rows[MAXN];
int g_n;
int g_ord[MAXN];
int g_sel[MAXN];
int g_sel_n;
int g_spent;
int g_budget;
char g_origin[32];
Sheet g_sheets[MAXN];
int g_nsheets;
ChgFile g_chgf[8];
int g_nchgf;

static void trim_nl(char *s)
{
	size_t n = strlen(s);

	while (n > 0 && (s[n - 1] == '\n' || s[n - 1] == '\r')) {
		s[--n] = 0;
	}
}

static int parse_lines(char *rest, int *out, int cap)
{
	int n = 0;
	char *tok;

	tok = strtok(rest, " \t");
	while (tok && n < cap) {
		out[n++] = atoi(tok);
		tok = strtok(NULL, " \t");
	}
	return n;
}

static int load_ticks(void)
{
	FILE *fp;
	char line[128];
	char id[MAXID];
	int dur, i;

	fp = fopen("/app/durcards/ticks.txt", "r");
	if (!fp)
		return -1;
	while (fgets(line, sizeof line, fp)) {
		trim_nl(line);
		if (!line[0])
			continue;
		if (sscanf(line, "%31s %d", id, &dur) != 2)
			continue;
		for (i = 0; i < g_n; i++) {
			if (strcmp(g_rows[i].id, id) == 0)
				g_rows[i].dur = dur;
		}
	}
	fclose(fp);
	return 0;
}

static int load_sheet(const char *path)
{
	FILE *fp;
	char line[256];
	Sheet *sh;
	FileHit *fh = NULL;

	if (g_nsheets >= MAXN)
		return -1;
	sh = &g_sheets[g_nsheets];
	memset(sh, 0, sizeof *sh);
	fp = fopen(path, "r");
	if (!fp)
		return -1;
	while (fgets(line, sizeof line, fp)) {
		trim_nl(line);
		if (!line[0])
			continue;
		if (strncmp(line, "ID ", 3) == 0) {
			strncpy(sh->id, line + 3, MAXID - 1);
		} else if (strncmp(line, "FILE ", 5) == 0) {
			if (sh->nfiles >= 8)
				continue;
			fh = &sh->files[sh->nfiles++];
			memset(fh, 0, sizeof *fh);
			strncpy(fh->path, line + 5, MAXPATH - 1);
		} else if (strncmp(line, "HITS ", 5) == 0 && fh) {
			char buf[256];

			strncpy(buf, line + 5, sizeof buf - 1);
			fh->nlines = parse_lines(buf, fh->lines, MAXLN);
		} else if (strcmp(line, "END") == 0) {
			break;
		}
	}
	fclose(fp);
	if (!sh->id[0])
		return -1;
	g_nsheets++;
	return 0;
}

static int load_meshes(void)
{
	DIR *d;
	struct dirent *ent;
	char path[256];

	d = opendir("/app/meshcards");
	if (!d)
		return -1;
	while ((ent = readdir(d)) != NULL) {
		size_t n = strlen(ent->d_name);

		if (n < 6 || strcmp(ent->d_name + n - 5, ".mesh") != 0)
			continue;
		snprintf(path, sizeof path, "/app/meshcards/%s", ent->d_name);
		if (load_sheet(path) != 0) {
			closedir(d);
			return -1;
		}
	}
	closedir(d);
	return 0;
}

int load_card(const char *path)
{
	FILE *fp;
	char line[256];
	ChgFile *cf = NULL;

	memset(g_rows, 0, sizeof g_rows);
	g_n = 0;
	g_nsheets = 0;
	g_nchgf = 0;
	g_budget = 0;
	g_origin[0] = 0;
	g_sel_n = 0;
	g_spent = 0;
	fp = fopen(path, "r");
	if (!fp)
		return -1;
	while (fgets(line, sizeof line, fp)) {
		trim_nl(line);
		if (!line[0])
			continue;
		if (strncmp(line, "BUDGET ", 7) == 0) {
			g_budget = atoi(line + 7);
		} else if (strncmp(line, "ORIGIN ", 7) == 0) {
			strncpy(g_origin, line + 7, sizeof g_origin - 1);
		} else if (strncmp(line, "FILE ", 5) == 0) {
			if (g_nchgf >= 8)
				continue;
			cf = &g_chgf[g_nchgf++];
			memset(cf, 0, sizeof *cf);
			strncpy(cf->path, line + 5, MAXPATH - 1);
		} else if (strncmp(line, "LINES ", 6) == 0 && cf) {
			char buf[256];

			strncpy(buf, line + 6, sizeof buf - 1);
			cf->nlines = parse_lines(buf, cf->lines, MAXLN);
		} else if (strcmp(line, "END") == 0) {
			break;
		}
	}
	fclose(fp);
	if (load_meshes() != 0)
		return -1;
	g_n = g_nsheets;
	{
		int i;

		for (i = 0; i < g_n; i++) {
			strncpy(g_rows[i].id, g_sheets[i].id, MAXID - 1);
			g_rows[i].w = 0;
			g_rows[i].dur = 0;
		}
	}
	return load_ticks();
}
