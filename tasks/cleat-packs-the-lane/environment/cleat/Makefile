BIN := /opt/ferry/bin/cleat
GO ?= go

.PHONY: all install clean

all: install

install:
	mkdir -p /opt/ferry/bin
	$(GO) build -o $(BIN) .

clean:
	rm -f $(BIN)
