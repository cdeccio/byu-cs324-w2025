CC = gcc
CFLAGS = -Wall -O2 -g

.PHONY: all
all: slow

slow: slow.c
	$(CC) $(CFLAGS) -o slow slow.c

.PHONY: clean
clean:
	rm -f slow
