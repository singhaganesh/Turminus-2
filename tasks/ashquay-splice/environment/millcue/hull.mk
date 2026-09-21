CC ?= gcc
CFLAGS ?= -O2 -Wall -Wextra -I/app/millcue -I/app/hopbag -I/app/objbay -I/app/ribvat -I/app/sidelog
SRC := /app/millcue/main.c /app/millcue/go.c /app/millcue/fin.c \
	/app/hopbag/op_bag.c /app/objbay/n_pick.c /app/objbay/readwell.c \
	/app/ribvat/n_credit.c /app/sidelog/retry.c
BIN := /app/bin/ashquay

.PHONY: hull
hull:
	mkdir -p /app/bin /app/outkeg
	$(CC) $(CFLAGS) -o $(BIN) $(SRC)
