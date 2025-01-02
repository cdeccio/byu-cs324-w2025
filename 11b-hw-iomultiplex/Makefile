CC = gcc
CFLAGS = -Wall -O2 -g -I ../include/

.PHONY: all
all: echoservere

echoservere: echoservere.c ../code/sockhelper.c
	$(CC) $(CFLAGS) -o echoservere echoservere.c ../code/sockhelper.c

.PHONY: clean
clean:
	rm -f echoservere
