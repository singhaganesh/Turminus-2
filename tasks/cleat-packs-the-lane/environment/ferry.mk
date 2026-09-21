.PHONY: all clean rebuild cleat

all: cleat

cleat:
	$(MAKE) -C /app/environment install

rebuild: clean all

clean:
	$(MAKE) -C /app/environment clean
