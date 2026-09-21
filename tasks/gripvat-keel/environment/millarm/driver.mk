CC = gcc
OUT ?= /app/bin/keelgrip
CFLAGS = -O2 -Wall -I/app/millarm -I/app/rootwell -I/app/adjmill -I/app/softbay -I/app/ridget -I/app/twinline
OBJS = driver.o latch.o load.o \
	/app/rootwell/scan.o \
	/app/softbay/skip.o \
	/app/ridget/step.o \
	/app/twinline/note.o

.PHONY: hull

hull: $(OUT)

$(OUT): $(OBJS)
	mkdir -p $(dir $(OUT))
	$(CC) $(CFLAGS) -o $@ $(OBJS)

driver.o: driver.c
	$(CC) $(CFLAGS) -c driver.c -o driver.o

latch.o: latch.c
	$(CC) $(CFLAGS) -c latch.c -o latch.o

load.o: load.c
	$(CC) $(CFLAGS) -c load.c -o load.o

/app/rootwell/scan.o: /app/rootwell/scan.c
	$(CC) $(CFLAGS) -c /app/rootwell/scan.c -o /app/rootwell/scan.o

/app/softbay/skip.o: /app/softbay/skip.c
	$(CC) $(CFLAGS) -c /app/softbay/skip.c -o /app/softbay/skip.o

/app/ridget/step.o: /app/ridget/step.c /app/ridget/step.inc
	$(CC) $(CFLAGS) -c /app/ridget/step.c -o /app/ridget/step.o

/app/twinline/note.o: /app/twinline/note.c
	$(CC) $(CFLAGS) -c /app/twinline/note.c -o /app/twinline/note.o
