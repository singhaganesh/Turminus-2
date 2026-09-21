static int nbor_ord(const void *x, const void *y)
{
	const Edge *a = *(const Edge * const *)x;
	const Edge *b = *(const Edge * const *)y;
	return (int)a->to - (int)b->to;
}
