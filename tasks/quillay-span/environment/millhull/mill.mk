CXX ?= g++
CC ?= gcc
CFLAGS ?= -O2 -Wall -Wextra -I/app/millhull -I/app/cuewell -I/app/wickdesk -I/app/offpack
CXXFLAGS ?= -O2 -Wall -Wextra -std=c++17 -I/app/millhull -I/app/cuewell -I/app/wickdesk -I/app/offpack
BIN := /app/bin/quillay

.PHONY: hull
# WAVE: tamp compiles /app/spanhearth/load.c with gcc -DWAVE from wave.txt
hull:
	mkdir -p /app/bin /app/wickbin /app/hearthbin
	$(CC) $(CFLAGS) -c /app/offpack/sum.c -o /tmp/sum.o
	$(CXX) $(CXXFLAGS) -o $(BIN) /app/millhull/main.cc /app/millhull/drive.cc \
	  /app/millhull/op_bind.cc /app/millhull/elfbits.cc \
	  /app/cuewell/op_halt.cc /app/wickdesk/op_mesh.cc \
	  /app/offpack/stamp.cc /tmp/sum.o
