#include "store.h"

LockRec G[MAXL];
int GN;
int g_closer;
int PLAN[MAXL];
int PN;
int succ[MAXL][MAXL];
int nsucc[MAXL];
char g_path[256];
