CC = gcc
CFLAGS = -Wall -O2 -g -I ../include/

.PHONY: all
all: client server

client: client.c ../code/sockhelper.c
	$(CC) $(CFLAGS) -o client client.c ../code/sockhelper.c

server: server.c ../code/sockhelper.c
	$(CC) $(CFLAGS) -o server server.c ../code/sockhelper.c

.PHONY: clean
clean:
	rm -f client server
