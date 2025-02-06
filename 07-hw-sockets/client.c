#include <arpa/inet.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>

#include "sockhelper.h"

#define BUF_SIZE 500

int main(int argc, char *argv[]) {

	// Check usage
	if (argc < 3 ||
		((strcmp(argv[1], "-4") == 0 || strcmp(argv[1], "-6") == 0) &&
			argc < 4)) {
		fprintf(stderr, "Usage: %s [ -4 | -6 ] host port msg...\n", argv[0]);
		exit(EXIT_FAILURE);
	}

	// Use only IPv4 (AF_INET) if -4 is specified;
	// Use only IPv6 (AF_INET6) if -6 is specified;
	// Try both if neither is specified.
	int af = AF_UNSPEC;
	int hostindex;
	if (strcmp(argv[1], "-4") == 0 ||
			strcmp(argv[1], "-6") == 0) {
		if (strcmp(argv[1], "-6") == 0) {
			af = AF_INET6;
		} else { // (strcmp(argv[1], "-4") == 0) {
			af = AF_INET;
		}
		hostindex = 2;
	} else {
		hostindex = 1;
	}


	/* SECTION A - pre-socket setup; getaddrinfo() */

	// Declare and initialize hints, which is passed to getaddrinfo() to
	// get our address info.
	struct addrinfo hints;
	// Initialize everything to 0
	memset(&hints, 0, sizeof(struct addrinfo));
	// Set the address family to either AF_INET (get only IPv4 address
	// information), AF_INET6 (get only IPv6 information), or AF_UNSPEC
	// (get both IPv4 and IPv6 information), depending on what was passed
	// in on the command line.
	hints.ai_family = af;
	// Use type SOCK_DGRAM (UDP)
	hints.ai_socktype = SOCK_DGRAM;


	struct addrinfo *result;
	int s;
	s = getaddrinfo(argv[hostindex],
			argv[hostindex + 1], &hints, &result);
	if (s != 0) {
		fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(s));
		exit(EXIT_FAILURE);
	}


	/* SECTION B - set up socket using results from getaddrinfo */

	int sfd;
	int addr_fam;
	socklen_t addr_len;

	// Local address information is stored in local_addr_ss, which is of
	// type struct addr_storage.  However, all functions require a
	// parameter of type struct sockaddr *.  Instead of type-casting
	// everywhere, we declare local_addr, which is of type
	// struct sockaddr *, point it to the address of local_addr_ss, and use
	// local_addr everywhere.
	struct sockaddr_storage local_addr_ss;
	struct sockaddr *local_addr = (struct sockaddr *)&local_addr_ss;
	char local_ip[INET6_ADDRSTRLEN];
	unsigned short local_port;

	// Remote address information is stored in remote_addr_ss.  See notes
	// above for local_addr_ss and local_addr_ss.
	struct sockaddr_storage remote_addr_ss;
	struct sockaddr *remote_addr = (struct sockaddr *)&remote_addr_ss;
	char remote_ip[INET6_ADDRSTRLEN];
	unsigned short remote_port;

	struct addrinfo *rp;
	for (rp = result; rp != NULL; rp = rp->ai_next) {
		// Loop through every entry in the linked list populated by
		// getaddrinfo().   If either socket(2) or connect(2) fails, we
		// close the socket and try the next address.
		//
		// For each iteration of the loop, rp points to an instance of
		// struct * addrinfo that contains the following members:
		//
		// ai_family: The address family for the given address. This is
		//         either AF_INET (IPv4) or AF_INET6 (IPv6).
		// ai_socktype: The type of socket.  This is either SOCK_DGRAM
		//         or SOCK_STREAM.
		// ai_addrlen: The length of the structure used to hold the
		//         address (different for AF_INET and AF_INET6).
		// ai_addr: The struct sockaddr_storage that holds the IPv4 or
		//         IPv6 address and port.

		sfd = socket(rp->ai_family, rp->ai_socktype, 0);
		if (sfd < 0) {
			// error creating the socket
			continue;
		}

		addr_fam = rp->ai_family;
		addr_len = rp->ai_addrlen;
		// Copy the value of rp->ai_addr to the struct sockaddr_storage
		// pointed to by remote_addr.
		memcpy(remote_addr, rp->ai_addr, sizeof(struct sockaddr_storage));

		// Extract the IP address (as a string) and port (as an int)
		// from the struct referred to by remote_addr, and store them
		// in the locations referred to by remote_ip and &remote_port.
		// This is a little messy, so we use the helper function
		// parse_sockaddr(), which is defined in ../code/sockhelper.c.
		parse_sockaddr(remote_addr, remote_ip, &remote_port);
		fprintf(stderr, "Connecting to %s:%d (addr family: %d)\n",
				remote_ip, remote_port, addr_fam);

		// If connect() succeeds, then break out of the loop; we will
		// use the current address as our remote address.
		if (connect(sfd, remote_addr, addr_len) >= 0)
			break;

		close(sfd);
	}

	if (rp == NULL) {
		// If rp is NULL, then connect() did not succeed with any
		// address returned by getaddrinfo().
		fprintf(stderr, "Could not connect\n");
		exit(EXIT_FAILURE);
	}

	// Free the memory associated with the linked list populated by
	// getaddrinfo()
	freeaddrinfo(result);

	// Extract the local IP address and port associated with sfd into the
	// struct sockaddr_storage referenced by local_addr.  This is done
	// using the system call getsockname().
	//
	// NOTE: addr_len needs to be initialized before every call to
	// getsockname().  See the man page for getsockname().
	addr_len = sizeof(struct sockaddr_storage);
	s = getsockname(sfd, local_addr, &addr_len);

	// Extract the IP address (as a string) and port (as an int)
	// from the struct referred to by local_addr, and store them
	// in the locations referred to by local_ip and &local_port.
	// This is a little messy, so we use the helper function
	// parse_sockaddr(), which is defined in ../code/sockhelper.c.
	parse_sockaddr(local_addr, local_ip, &local_port);
	fprintf(stderr, "Local socket info: %s:%d (addr family: %d)\n",
			local_ip, local_port, addr_fam);


	/* SECTION C - interact with server; send, receive, print messages */

	// Send remaining command-line arguments as separate
	// datagrams, and read responses from server.
	for (int j = hostindex + 2; j < argc; j++) {
		// buf will hold the bytes we read from the socket.
		char buf[BUF_SIZE];

		size_t len = strlen(argv[j]);

		// Check for buffer overflow.
		if (len > BUF_SIZE) {
			fprintf(stderr,
					"Ignoring long message in argument %d\n", j);
			continue;
		}

		// Send bytes to remote socket using send().
		ssize_t nwritten = send(sfd, argv[j], len, 0);
		if (nwritten < 0) {
			perror("send");
			exit(EXIT_FAILURE);
		}
		printf("Sent %zd bytes: %s\n", len, argv[j]);

		// Read bytes from remote socket using recv().
		ssize_t nread = recv(sfd, buf, BUF_SIZE, 0);
		buf[nread] = '\0';
		if (nread < 0) {
			perror("read");
			exit(EXIT_FAILURE);
		}
		printf("Received %zd bytes: %s\n", nread, buf);

	}

	exit(EXIT_SUCCESS);
}
