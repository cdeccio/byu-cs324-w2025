CC = gcc
CFLAGS = -Wall -O2 -g -I ../include/

all: treasure_hunter
.PHONY: all

treasure_hunter: treasure_hunter.c ../code/sockhelper.c
	$(CC) $(CFLAGS) -o treasure_hunter treasure_hunter.c ../code/sockhelper.c

.PHONY: clean
clean:
	rm -f treasure_hunter
