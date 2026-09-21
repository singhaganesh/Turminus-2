CC = gcc
OUT ?= /app/bin/flaxcord
CFLAGS = -O2 -Wall -I/app/flaxcli -I/app/cordspin -I/app/chunkvat -I/app/emitbay -I/app/differbay -I/app/unreelkit
OBJS = hull.o serial.o token.o \
	/app/cordspin/bag.o \
	/app/chunkvat/walk.o \
	/app/emitbay/pour.o \
	/app/differbay/cmp.o \
	/app/unreelkit/show.o

.PHONY: hull

hull: $(OUT)

$(OUT): $(OBJS)
	mkdir -p $(dir $(OUT))
	$(CC) $(CFLAGS) -o $@ $(OBJS)

hull.o: hull.c
	$(CC) $(CFLAGS) -c hull.c -o hull.o

serial.o: serial.c
	$(CC) $(CFLAGS) -c serial.c -o serial.o

token.o: token.c
	$(CC) $(CFLAGS) -c token.c -o token.o

/app/cordspin/bag.o: /app/cordspin/bag.c
	$(CC) $(CFLAGS) -c /app/cordspin/bag.c -o /app/cordspin/bag.o

/app/chunkvat/walk.o: /app/chunkvat/walk.c
	$(CC) $(CFLAGS) -c /app/chunkvat/walk.c -o /app/chunkvat/walk.o

/app/emitbay/pour.o: /app/emitbay/pour.c
	$(CC) $(CFLAGS) -c /app/emitbay/pour.c -o /app/emitbay/pour.o

/app/differbay/cmp.o: /app/differbay/cmp.c
	$(CC) $(CFLAGS) -c /app/differbay/cmp.c -o /app/differbay/cmp.o

/app/unreelkit/show.o: /app/unreelkit/show.c
	$(CC) $(CFLAGS) -c /app/unreelkit/show.c -o /app/unreelkit/show.o
