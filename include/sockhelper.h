#include <sys/socket.h>

sa_family_t get_addr_fam(int sock);
int populate_sockaddr(struct sockaddr *, sa_family_t,
		const char *, unsigned short);
int parse_sockaddr(const struct sockaddr *,
		char *, unsigned short *);
