#include <sys/types.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netdb.h>
#include <arpa/inet.h>

#include "sockhelper.h"

#define BUF_SIZE 500

int main(int argc, char *argv[]) {

	/* Check usage */
	if (!(argc == 2 || (argc == 3 &&
			(strcmp(argv[1], "-4") == 0 || strcmp(argv[1], "-6") == 0)))) {
		fprintf(stderr, "Usage: %s [ -4 | -6 ] port\n", argv[0]);
		exit(EXIT_FAILURE);
	}

	int portindex;
	if (argc == 2) {
		portindex = 1;
	} else {
		portindex = 2;
	}

	/* Use IPv4 by default (or if -4 is specified);
	 * If -6 is specified, then use IPv6 instead. */
	int addr_fam;
	if (argc == 2 || strcmp(argv[1], "-4") == 0) {
		addr_fam = AF_INET;
	} else {
		addr_fam = AF_INET6;
	}

	unsigned short port = atoi(argv[portindex]);
	int sock_type = SOCK_DGRAM;

	/* SECTION A - populate address structures */

	/* SECTION B - setup socket */

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


	/* SECTION C - interact with clients; receive and send messages */

	// Read datagrams and echo them back to sender
	while (1) {
		char buf[BUF_SIZE];

		// Declare structures for remote address and port.
		// See notes above for local_addr_ss and local_addr_ss.
		struct sockaddr_storage remote_addr_ss;
		struct sockaddr *remote_addr = (struct sockaddr *)&remote_addr_ss;
		char remote_ip[INET6_ADDRSTRLEN];
		unsigned short remote_port;

		// NOTE: addrlen needs to be initialized before every call to
		// recvfrom().  See the man page for recvfrom().
		socklen_t addr_len = sizeof(struct sockaddr_storage);
		ssize_t nread = recvfrom(sfd, buf, BUF_SIZE, 0,
				remote_addr, &addr_len);
		if (nread < 0) {
			perror("receiving message");
			exit(EXIT_FAILURE);
		}

		// Extract the IP address and port from remote_addr using
		// parse_sockaddr().  parse_sockaddr() is defined in
		// ../code/sockhelper.c.
		parse_sockaddr(remote_addr, remote_ip, &remote_port);
		printf("Received %zd bytes from %s:%d\n",
				nread, remote_ip, remote_port);

		if (sendto(sfd, buf, nread, 0, remote_addr, addr_len) < 0) {
			perror("sending response");
		}
	}
}
