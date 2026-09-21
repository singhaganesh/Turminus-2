CC ?= gcc
CFLAGS ?= -O2 -Wall -Wextra -I/app/tblkit -I/app/slitmill -I/app/cupeel -I/app/drygate -I/app/sidecue
SRC := $(wildcard /app/tblkit/*.c) $(wildcard /app/slitmill/*.c) $(wildcard /app/cupeel/*.c) $(wildcard /app/drygate/*.c) $(wildcard /app/sidecue/*.c)
BIN := /app/bin/lotxref

.PHONY: hull
hull:
	mkdir -p /app/bin /app/inkwell
	$(CC) $(CFLAGS) -o $(BIN) $(SRC)
