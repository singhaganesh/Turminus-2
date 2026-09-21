CC = gcc
CFLAGS = -O0 -g -Wall -std=c11 -I/app
HULLBIN ?= /app/bin/rimlock
OBJS = main.o go.o rank.o \
	../knothub/store.o ../knothub/graph.o ../knothub/pick.o ../knothub/cycle.o \
	../readcue/scan.o \
	../inkurn/book.o \
	../emiturn/bind.o \
	../inkfold/fold.o

hull: $(OBJS)
	$(CC) $(CFLAGS) -o $(HULLBIN) $(OBJS)

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

../knothub/%.o: ../knothub/%.c
	$(CC) $(CFLAGS) -c -o $@ $<

../readcue/%.o: ../readcue/%.c
	$(CC) $(CFLAGS) -c -o $@ $<

../inkurn/%.o: ../inkurn/%.c
	$(CC) $(CFLAGS) -c -o $@ $<

../emiturn/%.o: ../emiturn/%.c
	$(CC) $(CFLAGS) -c -o $@ $<

../inkfold/%.o: ../inkfold/%.c
	$(CC) $(CFLAGS) -c -o $@ $<
