CC ?= gcc
CFLAGS ?= -O2 -Wall -Wextra -Iforgekit -I/app/millscore
SRC := $(wildcard forgekit/*.c) $(wildcard /app/millscore/*.c)
BIN := /app/bin/rivetbay

.PHONY: hull
hull:
	mkdir -p /app/bin
	$(CC) $(CFLAGS) -o $(BIN) $(SRC)
