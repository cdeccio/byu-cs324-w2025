CC = gcc
CFLAGS = -Wall -O2 -g -I ../include/

.PHONY: all
all: echoserveri echoserverp echoservert echoservert_pre

echoserveri: echoserveri.c echo.c ../code/sockhelper.c
	$(CC) $(CFLAGS) -o echoserveri echoserveri.c echo.c ../code/sockhelper.c

echoserverp: echoserverp.c echo.c ../code/sockhelper.c
	$(CC) $(CFLAGS) -o echoserverp echoserverp.c echo.c ../code/sockhelper.c

echoservert: echoservert.c echo.c ../code/sockhelper.c
	$(CC) $(CFLAGS) -o echoservert echoservert.c echo.c ../code/sockhelper.c -lpthread

echoservert_pre: echoservert_pre.c echo.c echo_cnt.c ../code/sbuf.c ../code/sockhelper.c
	$(CC) $(CFLAGS) -o echoservert_pre echoservert_pre.c echo.c echo_cnt.c ../code/sbuf.c ../code/sockhelper.c -lpthread

.PHONY: clean
clean:
	rm -f echoserveri echoserverp echoservert echoservert_pre
