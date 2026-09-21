CC = gcc
CFLAGS = -std=c11 -O2 -Wall -Wextra -D_POSIX_C_SOURCE=200809L -Iinclude
SRCS = src/main.c src/util.c src/scan.c select/roster.c src/tidy.c intake/ledger.c
BIN = bin/anvil

.PHONY: all reforge clean

all: $(BIN)

$(BIN): $(SRCS) include/*.h
	mkdir -p bin var
	$(CC) $(CFLAGS) -o $(BIN) $(SRCS)

reforge: clean all

clean:
	rm -f $(BIN)
