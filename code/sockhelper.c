#include <stdlib.h>
#include <stdio.h>
#include <arpa/inet.h>

#include "sockhelper.h"

/*
 * Return the address family associated with a socket.
 */
sa_family_t get_addr_fam(int sock) {
	struct sockaddr_storage addr;
	socklen_t addr_len = sizeof(addr);
	if (getsockname(sock, (struct sockaddr*)&addr, &addr_len) < 0) {
		return -1;
	}
	return addr.ss_family;
}

/*
 * Populate a struct sockaddr with an IP address and port.
 *
 *   - addr: the address of (i.e., a pointer to) a struct sockaddr.
 *   - addr_fam: the address family associated with the IP address with which
 *     addr will be populated.  Only AF_INET (IPv4) and AF_INET6 (IPv6) are
 *     valid options.
 *   - ip: a string containing the presentation format of the IP address.  If
 *     ip is NULL, then the wildcard IP address ("0.0.0.0" for IPv4 or "::" for
 *     IPv6) is used. Passing NULL for ip is especially useful when preparing a
 *     struct sockaddr for calling bind().
 *   - port: the 16-bit (unsigned short) value of the port that should be used.
 *
 *   Return 0 if everything succeeded; -1 otherwise.
 */
int populate_sockaddr(struct sockaddr *addr, sa_family_t addr_fam,
		const char *ip, unsigned short port) {
	if (addr_fam == AF_INET) {
		// We are using IPv4.
		struct sockaddr_in *ipv4addr = (struct sockaddr_in *)addr;

		// Populate ipv4addr->sin_family with the address family
		// associated with the socket.
		ipv4addr->sin_family = addr_fam;
		if (ip == NULL) {
			// By default, bind to all local IPv4 addresses
			// (i.e., the IPv4 "wildcard" address)
			ip = "0.0.0.0";
		}

		// Use inet_pton() to populate ipv4addr->sin_addr.s_addr with
		// the bytes comprising the IPv4 address contained in ip.
		if (inet_pton(addr_fam, ip, &ipv4addr->sin_addr.s_addr) <= 0) {
			fprintf(stderr, "Error: invalid IPv4 address "
					"passed to bind_from_str(): %s\n", ip);
			exit(EXIT_FAILURE);
		}

		// Populate ipv4addr->sin_port with the specified port, in
		// network byte order.
		ipv4addr->sin_port = htons(port);
	} else if (addr_fam == AF_INET6) {
		// We are using IPv6.
		struct sockaddr_in6 *ipv6addr = (struct sockaddr_in6 *)addr;

		// Populate ipv6addr->sin6_family with the address family
		// associated with the socket.
		ipv6addr->sin6_family = addr_fam;
		if (ip == NULL) {
			// By default, bind to all local IPv6 addresses
			// (i.e., the IPv4 "wildcard" address)
			ip = "::";
		}

		// Use inet_pton() to populate ipv6addr->sin6_addr.s6_addr with
		// the bytes comprising the IPv6 address contained in ip.
		if (inet_pton(addr_fam, ip, &ipv6addr->sin6_addr.s6_addr) <= 0) {
			fprintf(stderr, "Error: invalid IPv6 address "
					"passed to bind_from_str(): %s\n", ip);
			exit(EXIT_FAILURE);
		}

		// Populate ipv6addr->sin6_port with the specified port, in
		// network byte order.
		ipv6addr->sin6_port = htons(port);
	} else {
		// TODO account for other address families
		return -1;
	}
	return 0;
}

/*
 * Extract the IP address and port from a struct sockaddr.
 *
 *   - addr: the address of (i.e., a pointer to) a struct sockaddr.
 *   - ip: a string (char *) to be populated with the presentation format of
 *     the IP address extracted from addr.  The size of the array pointed to by
 *     ip should be at least INET_ADDRSTRLEN for IPv4 or INET6_ADDRSTRLEN for
 *     IPv6.  Note that INET6_ADDRSTRLEN should be big enough for either.
 *   - port: the address of (i.e., a pointer to) an unsigned short to be
 *     populated with the value of the port extracted from addr.
 *
 *   Return 0 if everything succeeded; -1 otherwise.
 */
int parse_sockaddr(const struct sockaddr *addr, char *ip, unsigned short *port) {
	sa_family_t addr_fam = addr->sa_family;
	if (addr_fam == AF_INET) {
		// We are using IPv4.
		struct sockaddr_in *ipv4addr = (struct sockaddr_in *)addr;

		// Populate ip with the presentation format of the IPv4
		// address.
		inet_ntop(addr_fam, &ipv4addr->sin_addr, ip, INET6_ADDRSTRLEN);

		// Populate port with the value of the port, converted to host
		// byte order.
		*port = ntohs(ipv4addr->sin_port);
	} else if (addr_fam == AF_INET6) {
		// We are using IPv6.
		struct sockaddr_in6 *ipv6addr = (struct sockaddr_in6 *)addr;

		// Populate ip with the presentation format of the IPv6
		// address.
		inet_ntop(addr_fam, &ipv6addr->sin6_addr,
				ip, INET6_ADDRSTRLEN);

		// Populate port with the value of the port, converted to host
		// byte order.
		*port = ntohs(ipv6addr->sin6_port);
	} else {
		// TODO account for other address families
		return -1;
	}
	return 0;
}
