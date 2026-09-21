#include "emit.h"

void cfg_emit(FILE *fp)
{
	fputs("static int nbor_ord(const void *x, const void *y)\n", fp);
	fputs("{\n", fp);
	fputs("\tconst Edge *a = *(const Edge * const *)x;\n", fp);
	fputs("\tconst Edge *b = *(const Edge * const *)y;\n", fp);
	fputs("\treturn (int)a->to - (int)b->to;\n", fp);
	fputs("}\n", fp);
}
