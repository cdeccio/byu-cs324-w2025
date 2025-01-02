CC = gcc
CFLAGS = -Wall -O2 -g -I ../include/

.PHONY: all
all: proxy

proxy: proxy.c ../code/sbuf.c ../code/sockhelper.c
	$(CC) $(CFLAGS) -o proxy proxy.c ../code/sbuf.c ../code/sockhelper.c

.PHONY: clean
clean:
	rm -f proxy
