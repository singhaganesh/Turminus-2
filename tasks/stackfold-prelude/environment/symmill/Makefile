CC ?= gcc
CFLAGS ?= -O2 -Wall -Wextra -fPIC
LDFLAGS ?= -Wl,--build-id
SRC := src/core.c src/worker.c src/dispatch_ring.c
OBJS := $(SRC:.c=.o)
TARGET := fold/runtime
SYMAP := fold/runtime.symmap
PROFILE := fold/profile.json
PCFOLD := /app/bin/pcfold
SAMPLES := /app/benchframes/bench.samples

include mk/foldlink.dep

.PHONY: emitmap clean hull

# emitmap rebuilds runtime.symmap + profile.json from the current fold rule
hull: $(TARGET)

emitmap: $(PROFILE)
	@:

$(TARGET): $(OBJS)
	@mkdir -p fold
	$(CC) $(LDFLAGS) -o $@ $(OBJS)

$(PROFILE): $(SYMAP) $(SAMPLES)
	$(PCFOLD) render $(SAMPLES) $(SYMAP) -o $(PROFILE)

clean:
	rm -f $(OBJS) $(TARGET) $(SYMAP) $(PROFILE)

src/%.o: src/%.c
	$(CC) $(CFLAGS) -c -o $@ $<
