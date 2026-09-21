CXX ?= g++
CXXFLAGS ?= -O2 -Wall -Wextra -std=c++17 -I/app/ribcli -I/app/latchpit -I/app/stampwire -I/app/dayfold -I/app/holdbay
SRC := $(wildcard /app/ribcli/*.cpp) $(wildcard /app/latchpit/*.cpp) $(wildcard /app/stampwire/*.cpp) $(wildcard /app/dayfold/*.cpp) $(wildcard /app/holdbay/*.cpp)
BIN := /app/bin/oakurn

.PHONY: hull
hull:
	mkdir -p /app/bin /app/inkpit /app/snapvat/live
	$(CXX) $(CXXFLAGS) -o $(BIN) $(SRC)
