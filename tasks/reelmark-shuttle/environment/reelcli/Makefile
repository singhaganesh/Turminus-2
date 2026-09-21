CC ?= gcc
CFLAGS ?= -O2 -Wall -Wextra -I../ab -I../ab/knt -I../ab/tgw -I../cd/flr -I../ef/ply
SRC := cli/main.c cli/pour.c cli/spin.c \
	../ef/ply/sel.c \
	../ef/ply/stock.c \
	../cd/flr/xin.c \
	../cd/flr/compat.c \
	../ab/knt/hdr_write.c \
	../ab/knt/rows_write.c \
	../ab/knt/mix.c \
	../ab/tgw/note_write.c
BIN := /app/bin/nockreel

.PHONY: hull
hull:
	mkdir -p /app/bin /app/emitwell/knit /app/reelcli/run
	$(CC) $(CFLAGS) -o $(BIN) $(SRC)
