
#include <sys/types.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netdb.h>
#include <arpa/inet.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/epoll.h>

#include "sockhelper.h"

#define MAXEVENTS 64
#define MAXLINE 2048


struct client_info {
	int fd;
	int total_length;
	char desc[1024];
};

int main(int argc, char **argv) 
{
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

	// set listening file descriptor nonblocking
	if (fcntl(sfd, F_SETFL, fcntl(sfd, F_GETFL, 0) | O_NONBLOCK) < 0) {
		fprintf(stderr, "error setting socket option\n");
		exit(1);
	}

	int efd;
	if ((efd = epoll_create1(0)) < 0) {
		perror("Error with epoll_create1");
		exit(EXIT_FAILURE);
	}

	// allocate memory for a new struct client_info, and populate it with
	// info for the listening socket
	struct client_info *listener =
		malloc(sizeof(struct client_info));
	listener->fd = sfd;
	sprintf(listener->desc, "Listen file descriptor (accepts new clients)");

	// register the listening file descriptor for incoming events using
	// edge-triggered monitoring
	struct epoll_event event;
	event.data.ptr = listener;
	event.events = EPOLLIN | EPOLLET;
	if (epoll_ctl(efd, EPOLL_CTL_ADD, sfd, &event) < 0) {
		fprintf(stderr, "error adding event\n");
		exit(EXIT_FAILURE);
	}

	struct epoll_event events[MAXEVENTS];
	while (1) {
		// wait for event to happen (-1 == no timeout)
		int n = epoll_wait(efd, events, MAXEVENTS, -1);

		for (int i = 0; i < n; i++) {
			// grab the data structure from the event, and cast it
			// (appropriately) to a struct client_info *.
			struct client_info *active_client =
				(struct client_info *)(events[i].data.ptr);

			printf("New event for fd %d (%s)\n", active_client->fd, active_client->desc);

			if ((events[i].events & EPOLLERR) ||
					(events[i].events & EPOLLHUP) ||
					(events[i].events & EPOLLRDHUP)) {
				/* An error has occured on this fd */
				fprintf(stderr, "epoll error on %s\n", active_client->desc);
				close(active_client->fd);
				free(active_client);
				continue;
			}


			if (sfd == active_client->fd) {
				// loop until all pending clients have been accepted
				while (1) {
					// Declare structures for remote address and port.
					// See notes above for local_addr_ss and local_addr_ss.
					struct sockaddr_storage remote_addr_ss;
					struct sockaddr *remote_addr = (struct sockaddr *)&remote_addr_ss;
					char remote_ip[INET6_ADDRSTRLEN];
					unsigned short remote_port;

					socklen_t addr_len = sizeof(struct sockaddr_storage);
					int connfd = accept(active_client->fd, remote_addr, &addr_len);

					if (connfd < 0) {
						if (errno == EWOULDBLOCK ||
								errno == EAGAIN) {
							// no more clients ready to accept
							break;
						} else {
							perror("accept");
							exit(EXIT_FAILURE);
						}
					}

					parse_sockaddr(remote_addr, remote_ip, &remote_port);
					printf("Connection from %s:%d\n",
							remote_ip, remote_port);

					/* UNCOMMENT FOR NONBLOCKING
					// set client file descriptor nonblocking
					if (fcntl(connfd, F_SETFL, fcntl(connfd, F_GETFL, 0) | O_NONBLOCK) < 0) {
						fprintf(stderr, "error setting socket option\n");
						exit(1);
					}
					*/

					// allocate memory for a new struct
					// client_info, and populate it with
					// info for the new client
					struct client_info *new_client =
						(struct client_info *)malloc(sizeof(struct client_info));
					new_client->fd = connfd;
					new_client->total_length = 0;
					sprintf(new_client->desc, "Client %s:%d (fd %d)",
							remote_ip, remote_port, connfd);

					// register the client file descriptor
					// for incoming events using
					// edge-triggered monitoring
					event.data.ptr = new_client;
					event.events = EPOLLIN;
					if (epoll_ctl(efd, EPOLL_CTL_ADD, connfd, &event) < 0) {
						fprintf(stderr, "error adding event\n");
						exit(1);
					}
				}
			} else {
				// read from socket until (1) the remote side
				// has closed the connection or (2) there is no
				// data left to be read.
				/* UNCOMMENT FOR NONBLOCKING
				while (1) {
				*/
					char buf[MAXLINE];
					int len = recv(active_client->fd, buf, MAXLINE, 0);
					if (len == 0) { // EOF received
						// closing the fd will automatically
						// unregister the fd from the efd
						close(active_client->fd);
						free(active_client);
						/* UNCOMMENT FOR NONBLOCKING
						break;
						*/
					} else if (len < 0) {
						/* UNCOMMENT FOR NONBLOCKING
						if (errno == EWOULDBLOCK ||
								errno == EAGAIN) {
							// no more data to be read
						} else {
						*/
							perror("client recv");
							close(active_client->fd);
							free(active_client);
						/* UNCOMMENT FOR NONBLOCKING
						}
						break;
						*/
					} else {
						active_client->total_length += len;
						printf("Received %d bytes (total: %d)\n", len, active_client->total_length);
						send(active_client->fd, buf, len, 0);
					}
				/* UNCOMMENT FOR NONBLOCKING
				}
				*/
			}
		}
	}
	free(listener);
}
