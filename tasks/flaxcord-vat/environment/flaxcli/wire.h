#ifndef WIRE_H
#define WIRE_H

#include <stdint.h>

#define MAGIC "FLX1"
#define MAX_NM 256
#define MAX_FR 8
#define MAX_CH 64
#define MAX_LN 80

struct samp {
	char fr[MAX_FR][MAX_LN];
	int depth;
	uint32_t hits;
	uint32_t seq;
	char lab[MAX_LN];
};

#endif
