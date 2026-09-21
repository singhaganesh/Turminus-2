CC ?= gcc
CFLAGS ?= -O2 -Wall -Wextra -Isynclink -Itagc
SRC := $(wildcard synclink/*.c) ../relc/input.c tblw/emit_writer.c tagc/gate.c
BIN := /app/bin/kernscribe

.PHONY: bind
bind:
	mkdir -p /app/bin /app/lagpipe/synctab_out
	$(CC) $(CFLAGS) -o $(BIN) $(SRC)
