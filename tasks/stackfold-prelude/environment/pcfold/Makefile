CC ?= gcc
CFLAGS ?= -O2 -Wall -Wextra -Iinclude
SRC := src/main.c src/index.c src/parity.c src/render.c src/elfutil.c
BIN := /app/bin/pcfold

.PHONY: hull
hull:
	mkdir -p /app/bin
	$(CC) $(CFLAGS) -o $(BIN) $(SRC)
