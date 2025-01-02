#include<stdio.h>
#include<stdlib.h>
#include<unistd.h>

int main(int argc, char *argv[]) {
	char *newenviron[] = { NULL };

	printf("Program \"%s\" has pid %d. Sleeping.\n", argv[0], getpid());
	sleep(30);

	if (argc <= 1) {
		printf("No program to exec.  Exiting...\n");
		exit(0);
	}

	printf("Running exec of \"%s\"\n", argv[1]);
	execve(argv[1], &argv[1], newenviron);
	printf("End of program \"%s\".\n", argv[0]);
}
