#include<stdio.h>
#include<stdlib.h>
#include<unistd.h>

#define MAXARGS 10
#define PROG_PATH "/bin/cat"

int main(int argc, char *argv[]) {
	if (argc < 2) {
		fprintf(stderr, "Usage: %s <n> <prog_args...>\n", argv[0]);
		exit(1);
	}
	alarm(atoi(argv[1]));

	char *argv_new[MAXARGS];
	argv_new[0] = PROG_PATH;

	int i = 2;
	int j = i - 1;
	for (i = 2; i < argc; i++, j++) {
		if (j >= (MAXARGS - 1)) {
			break;
		}
		argv_new[j] = argv[i];
	}
	argv_new[j] = NULL;

	char *newenviron[] = { NULL };
	execve(argv_new[0], &argv_new[0], newenviron);
	fprintf(stderr, "error executing %s\n", PROG_PATH);
}
