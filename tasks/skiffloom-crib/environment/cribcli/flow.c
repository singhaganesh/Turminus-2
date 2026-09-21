#include "flow.h"

#include "../heapwell/rank.h"
#include "../tickpit/trim.h"
#include "../emitkit/pour.h"

int run_flow(const char *dest)
{
	op_lift();
	if (n_trim() != 0)
		return 1;
	return n_pour(dest);
}
