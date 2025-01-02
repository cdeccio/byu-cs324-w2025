/*
 * A thread-safe version of echo that counts the total number
 * of bytes received from clients.
 */

#include<semaphore.h>
#include<stdio.h>
#include<unistd.h>
#include<pthread.h>

#define MAXLINE 512

static int byte_cnt;  /* Byte counter */
static sem_t mutex;   /* and the mutex that protects it */

static void init_echo_cnt(void) {
	sem_init(&mutex, 0, 1);
	byte_cnt = 0;
}

void echo_cnt(int connfd) {
	size_t n;
	char buf[MAXLINE];
	static pthread_once_t once = PTHREAD_ONCE_INIT;

	pthread_once(&once, init_echo_cnt);

	while ((n = read(connfd, buf, MAXLINE)) > 0) {
		sem_wait(&mutex);
		byte_cnt += n;
		printf("server received %ld (%d total) bytes on fd %d\n",
				n, byte_cnt, connfd);
		sem_post(&mutex);

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
