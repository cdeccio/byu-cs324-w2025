#include<stdio.h>
#include<stdlib.h>
#include<unistd.h>

int main(int argc, char *argv[]) {
	int pid;

	printf("Starting program; process has pid %d\n", getpid());

	if ((pid = fork()) < 0) {
		fprintf(stderr, "Could not fork()");
		exit(1);
	}

	/* BEGIN SECTION A */

	printf("Section A;  pid %d\n", getpid());
	sleep(5);

	/* END SECTION A */
	if (pid == 0) {
		/* BEGIN SECTION B */

		printf("Section B\n");
		sleep(30);
		printf("Section B done sleeping\n");

		exit(0);

		/* END SECTION B */
	} else {
		/* BEGIN SECTION C */

		printf("Section C\n");
		sleep(60);
		printf("Section C done sleeping\n");

		exit(0);

		/* END SECTION C */
	}
	/* BEGIN SECTION D */

	printf("Section D\n");
	sleep(30);

	/* END SECTION D */
}

