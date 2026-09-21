#ifndef LOAD_H
#define LOAD_H

#include <stdint.h>

#define MAX_N 64
#define MAX_E 128
#define MAX_S 32

typedef struct {
	uint32_t id;
	char cls[MAX_S];
	uint32_t bytes;
} Node;

typedef struct {
	uint32_t from;
	uint32_t to;
	int kind;
	char field[MAX_S];
} Edge;

int load_card(const char *path);
void load_reset(void);
int load_ended(void);
int node_n(void);
int edge_n(void);
int site_n(void);
const Node *node_at(int i);
const Edge *edge_at(int i);
uint32_t site_at(int i);
const char *node_cls(uint32_t id);
uint32_t node_bytes(uint32_t id);
int node_index(uint32_t id);

#define KIND_WEAK 0
#define KIND_STRONG 1

#endif
