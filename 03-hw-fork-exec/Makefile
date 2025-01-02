CC = gcc
CFLAGS = -Wall -O2 -g

all: fork exec
.PHONY: all

fork: fork.c
	$(CC) $(CFLAGS) -o fork fork.c

exec: exec.c
	$(CC) $(CFLAGS) -o exec exec.c

.PHONY: clean
clean:
	rm -f fork exec
