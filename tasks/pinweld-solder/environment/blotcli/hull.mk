CC ?= gcc
CFLAGS ?= -O2 -Wall -Wextra -I. -I/app/tapdesk -I/app/recipath
SRC := $(wildcard *.c) $(wildcard /app/tapdesk/*.c) $(wildcard /app/recipath/*.c)
BIN := /app/bin/pinweld

.PHONY: hull
hull:
	mkdir -p /app/bin /app/mintbay
	$(CC) $(CFLAGS) -o $(BIN) $(SRC)
