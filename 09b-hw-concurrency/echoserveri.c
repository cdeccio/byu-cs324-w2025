/*
 * echoserveri.c - An iterative echo server
 */
#include <sys/types.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netdb.h>
#include <arpa/inet.h>

#include "sockhelper.h"

#define MAXLINE 8192

void echo(int connfd);

int main(int argc, char *argv[]) {

	/* Check usage */
	if (argc != 2) {
		fprintf(stderr, "Usage: %s port\n", argv[0]);
		exit(EXIT_FAILURE);
	}

	int addr_fam = AF_INET;
	int sock_type = SOCK_STREAM;

	unsigned short port = atoi(argv[1]);


	int sfd;
	if ((sfd = socket(addr_fam, sock_type, 0)) < 0) {
		perror("Error creating socket");
		exit(EXIT_FAILURE);
	}

	// Declare structures for local address and port.
	//
	// Address information is stored in local_addr_ss, which is of type
	// struct addr_storage.  However, all functions require a parameter of
	// type struct sockaddr *.  Instead of type-casting everywhere, we
	// declare local_addr, which is of type struct sockaddr *, point it to
	// the address of local_addr_ss, and use local_addr everywhere.
	struct sockaddr_storage local_addr_ss;
	struct sockaddr *local_addr = (struct sockaddr *)&local_addr_ss;

	// Populate local_addr with the port using populate_sockaddr().
	populate_sockaddr(local_addr, addr_fam, NULL, port);
	if (bind(sfd, local_addr, sizeof(struct sockaddr_storage)) < 0) {
		perror("Could not bind");
		exit(EXIT_FAILURE);
	}
	if (listen(sfd, 100) < 0) {
		perror("Could not listen");
		exit(EXIT_FAILURE);
	}


	while (1) {
		// Declare structures for remote address and port.
		// See notes above for local_addr_ss and local_addr_ss.
		struct sockaddr_storage remote_addr_ss;
		struct sockaddr *remote_addr = (struct sockaddr *)&remote_addr_ss;
		char remote_ip[INET6_ADDRSTRLEN];
		unsigned short remote_port;

		// NOTE: addrlen needs to be initialized before every call to
		// recvfrom().  See the man page for recvfrom().
		socklen_t addr_len = sizeof(struct sockaddr_storage);
		int connfd = accept(sfd, remote_addr, &addr_len);

		parse_sockaddr(remote_addr, remote_ip, &remote_port);
		printf("Connection from %s:%d\n",
				remote_ip, remote_port);

		echo(connfd);
		close(connfd);
	}
	exit(0);
}
