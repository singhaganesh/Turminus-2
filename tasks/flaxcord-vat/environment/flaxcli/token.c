#include "token.h"

#include <ctype.h>
#include <string.h>

void trim_copy(char *dst, const char *src, int cap)
{
	int n;

	if (!dst || cap <= 0)
		return;
	dst[0] = 0;
	if (!src)
		return;
	while (*src && isspace((unsigned char)*src))
		src++;
	strncpy(dst, src, (size_t)cap - 1);
	dst[cap - 1] = 0;
	n = (int)strlen(dst);
	while (n > 0 && isspace((unsigned char)dst[n - 1])) {
		dst[n - 1] = 0;
		n--;
	}
}
