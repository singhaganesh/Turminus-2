CC = gcc
OUT ?= /app/bin/skiffloom
CFLAGS = -O2 -Wall -I/app/cribcli -I/app/heapwell -I/app/spanurn -I/app/tickpit -I/app/emitkit
OBJS = hull.o latch.o load.o flow.o \
	/app/heapwell/rank.o \
	/app/spanurn/fold.o \
	/app/tickpit/trim.o \
	/app/emitkit/pour.o

.PHONY: hull

hull: $(OUT)

$(OUT): $(OBJS)
	mkdir -p $(dir $(OUT))
	$(CC) $(CFLAGS) -o $@ $(OBJS)

hull.o: hull.c
	$(CC) $(CFLAGS) -c hull.c -o hull.o

latch.o: latch.c
	$(CC) $(CFLAGS) -c latch.c -o latch.o

load.o: load.c
	$(CC) $(CFLAGS) -c load.c -o load.o

flow.o: flow.c
	$(CC) $(CFLAGS) -c flow.c -o flow.o

/app/heapwell/rank.o: /app/heapwell/rank.c
	$(CC) $(CFLAGS) -c /app/heapwell/rank.c -o /app/heapwell/rank.o

/app/spanurn/fold.o: /app/spanurn/fold.c
	$(CC) $(CFLAGS) -c /app/spanurn/fold.c -o /app/spanurn/fold.o

/app/tickpit/trim.o: /app/tickpit/trim.c
	$(CC) $(CFLAGS) -c /app/tickpit/trim.c -o /app/tickpit/trim.o

/app/emitkit/pour.o: /app/emitkit/pour.c
	$(CC) $(CFLAGS) -c /app/emitkit/pour.c -o /app/emitkit/pour.o
