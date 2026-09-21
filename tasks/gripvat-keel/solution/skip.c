#include "skip.h"

#include "../millarm/load.h"

int n_soft(int kind)
{
	if (kind == KIND_STRONG)
		return 1;
	if (kind == KIND_WEAK)
		return 0;
	return 0;
}
