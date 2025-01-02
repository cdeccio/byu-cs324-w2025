CC = gcc
# Do NOT use -O2 for compiler optimization!
CFLAGS = -Wall -g

.PHONY: all
all: signals killer

killer: killer.c
	$(CC) $(CFLAGS) -o killer killer.c

signals: signals.c
	$(CC) $(CFLAGS) -o signals signals.c

.PHONY: test
test:
	./driver.py

.PHONY: clean
clean:
	rm -f signals killer
