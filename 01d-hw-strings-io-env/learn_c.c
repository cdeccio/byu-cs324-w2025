#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include <fcntl.h>

#define BUFSIZE 30

void memprint(char *, char *, int);

void intro();
void part1();
void part2();
void part3();
void part4();
void part5(char *);
void part6();

int main(int argc, char *argv[]) {
	if (argc != 2) {
		fprintf(stderr, "usage: %s <filename>\n", argv[0]);
		exit(1);
	}
	intro();
	part1();
	part2();
	part3();
	part4();
	part5(argv[1]);
	part6();
}

void memprint(char *s, char *fmt, int len) {
	// iterate through each byte/character of s, and print each out
	int i;
	char fmt_with_space[8];

	sprintf(fmt_with_space, "%s ", fmt);
	for (i = 0; i < len; i++) {
		printf(fmt_with_space, s[i]);
	}
	printf("\n");
}

void intro() {
	printf("===== Intro =====\n");

	// Note: STDOUT_FILENO is defined in /usr/include/unistd.h:
	// #define	STDOUT_FILENO	1

	char s1[] = { 0x68, 0x65, 0x6c, 0x6c, 0x6f, 0x0a };
	write(STDOUT_FILENO, s1, 6);

	char s2[] = { 0xe5, 0x8f, 0xb0, 0xe7, 0x81, 0xa3, 0x0a };
	write(STDOUT_FILENO, s2, 7);

	char s3[] = { 0xf0, 0x9f, 0x98, 0x82, 0x0a };
	write(STDOUT_FILENO, s3, 5);
}

void part1() {

	printf("===== Question 1 =====\n");
	char s1[] = "hello";
	int s1_len;

	printf("===== Question 2 =====\n");

	printf("===== Question 3 (no code changes) =====\n");

	printf("===== Question 4 (no code changes) =====\n");

	printf("===== Question 5 =====\n");
	char s2[10];
	int s2_len;

	printf("===== Question 6 =====\n");
	char *s3 = s1;
	int s3_len;

	printf("===== Question 7 =====\n");
	char *s4 = malloc(1024 * sizeof(char));
	int s4_len;

	printf("===== Question 8 (no code changes) =====\n");

	printf("===== Question 9 =====\n");

}

void part2() {
	char s1[] = "hello";
	char s2[1024];
	char *s3 = s1;

	// Copy sizeof(s1) bytes of s1 to s2.
	memcpy(s2, s1, sizeof(s1));

	printf("===== Question 10 =====\n");

	printf("===== Question 11 =====\n");

	printf("===== Question 12 (no code changes) =====\n");

	printf("===== Question 13 =====\n");

	printf("===== Question 14 =====\n");

	printf("===== Question 15 =====\n");

	printf("===== Question 16 =====\n");
	s1[1] = 'u';

	printf("===== Question 17 =====\n");

	printf("===== Question 18 =====\n");
}

void part3() {
	char s1[] = { 'a', 'b', 'c', 'd', 'e', 'f' };
	char s2[] = { 97, 98, 99, 100, 101, 102 };
	char s3[] = { 0x61, 0x62, 0x63, 0x64, 0x65, 0x66 };

	printf("===== Question 19 =====\n");
}

void part4() {
	char s1[] = { 'a', 'b', 'c', '\0', 'd', 'e', 'f', '\0' };
	char s2[] = { 'a', 'b', 'c', '\0', 'x', 'y', 'z', '\0' };

	printf("===== Question 20 =====\n");

	printf("===== Question 21 =====\n");

	printf("===== Question 22 =====\n");
	char s3[16];
	char s4[16];

	printf("===== Question 23 =====\n");

	printf("===== Question 24 =====\n");
	int myval = 42;

	printf("===== Question 25 =====\n");
	char *s5;
	char *s6 = NULL;
	char *s7 = s4;

}

void part5(char *filename) {
	printf("===== Question 26 =====\n");

	printf("===== Question 27 =====\n");

	char buf[BUFSIZE];

	printf("===== Question 28 =====\n");

	fprintf(stderr, "===== Question 29 =====\n");

	printf("===== Question 30 (no code changes) =====\n");

	printf("===== Question 31 =====\n");
	int fd1, fd2;

	printf("===== Question 32 =====\n");
	size_t nread = 0;
	size_t totread = 0;

	printf("===== Question 33 (no code changes) =====\n");

	printf("===== Question 34 =====\n");

	printf("===== Question 35 (no code changes) =====\n");

	printf("===== Question 36 (no code changes) =====\n");

	printf("===== Question 37 =====\n");

	printf("===== Question 38 (no code changes) =====\n");

	printf("===== Question 39 (no code changes) =====\n");

	printf("===== Question 40 (no code changes) =====\n");

	printf("===== Question 41 =====\n");

	printf("===== Question 42 =====\n");

	printf("===== Question 43 =====\n");

	printf("===== Question 44 =====\n");

	printf("===== Question 45 =====\n");
	int ret = 0;

	printf("===== Question 46 =====\n");

	printf("===== Question 47 =====\n");

}

void part6() {
	printf("===== Question 48 =====\n");
	char *s1;

	printf("===== Question 49 (no code changes) =====\n");
	
}
