#ifndef WIRE_H
#define WIRE_H

#define MAXN 64
#define MAXID 32
#define MAXPATH 64
#define MAXHIT 256
#define MAXLN 32

typedef struct {
	char id[MAXID];
	int w;
	int dur;
} Row;

typedef struct {
	char path[MAXPATH];
	int lines[MAXLN];
	int nlines;
} FileHit;

typedef struct {
	char id[MAXID];
	FileHit files[8];
	int nfiles;
} Sheet;

typedef struct {
	char path[MAXPATH];
	int lines[MAXLN];
	int nlines;
} ChgFile;

extern Row g_rows[MAXN];
extern int g_n;
extern int g_ord[MAXN];
extern int g_sel[MAXN];
extern int g_sel_n;
extern int g_spent;
extern int g_budget;
extern char g_origin[32];
extern Sheet g_sheets[MAXN];
extern int g_nsheets;
extern ChgFile g_chgf[8];
extern int g_nchgf;
extern int g_latch;

#endif
