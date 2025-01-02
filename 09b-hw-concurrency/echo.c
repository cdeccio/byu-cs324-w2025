/*
 * echo - read and echo text lines until client closes connection
 */

#include <stdio.h>
#include <unistd.h>

#define MAXLINE 512

void echo(int connfd) {
    size_t n;
    char buf[MAXLINE];

    while ((n = read(connfd, buf, MAXLINE)) > 0) {
	printf("server received %d bytes\n", (int)n);

	int nsent = 0;
	int totsent = 0;
	while (nsent != n) {
		if ((nsent = write(connfd, buf + totsent, n - totsent)) < 0) {
			perror("write");
			break;
		}
		totsent += nsent;
	}
    }
    if (n < 0) {
	perror("read");
    }
}
