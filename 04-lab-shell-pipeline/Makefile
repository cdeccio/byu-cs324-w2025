# Makefile for the CS:APP Shell Lab

VERSION = 1
DRIVER = ./sdriver.pl
TESTDRIVER = ./checktsh.pl
TSH = ./tsh
TSHREF = ./tshref
TSHARGS = "-p"
CC = gcc
CFLAGS = -Wall -O2 -g
FILES = $(TSH) ./myintgroup ./myppid ./myspin ./mygrep ./mycat

all: $(FILES)

##################
# Regression tests
##################

# Compare output from student shell and reference shell
testall:
	$(TESTDRIVER) 1
test01:
	$(TESTDRIVER) -v -t trace01.txt
test02:
	$(TESTDRIVER) -v -t trace02.txt
test03:
	$(TESTDRIVER) -v -t trace03.txt
test34:
	$(TESTDRIVER) -v -t trace34.txt
test35:
	$(TESTDRIVER) -v -t trace35.txt
test36:
	$(TESTDRIVER) -v -t trace36.txt
test37:
	$(TESTDRIVER) -v -t trace37.txt
test38:
	$(TESTDRIVER) -v -t trace38.txt
test39:
	$(TESTDRIVER) -v -t trace39.txt
test40:
	$(TESTDRIVER) -v -t trace40.txt
test41:
	$(TESTDRIVER) -v -t trace41.txt
test42:
	$(TESTDRIVER) -v -t trace42.txt

# Run tests using the student's shell program
stest01:
	$(DRIVER) -t trace01.txt -s $(TSH) -a $(TSHARGS)
stest02:
	$(DRIVER) -t trace02.txt -s $(TSH) -a $(TSHARGS)
stest03:
	$(DRIVER) -t trace03.txt -s $(TSH) -a $(TSHARGS)
stest34:
	$(DRIVER) -t trace34.txt -s $(TSH) -a $(TSHARGS)
stest35:
	$(DRIVER) -t trace35.txt -s $(TSH) -a $(TSHARGS)
stest36:
	$(DRIVER) -t trace36.txt -s $(TSH) -a $(TSHARGS)
stest37:
	$(DRIVER) -t trace37.txt -s $(TSH) -a $(TSHARGS)
stest38:
	$(DRIVER) -t trace38.txt -s $(TSH) -a $(TSHARGS)
stest39:
	$(DRIVER) -t trace39.txt -s $(TSH) -a $(TSHARGS)
stest40:
	$(DRIVER) -t trace40.txt -s $(TSH) -a $(TSHARGS)
stest41:
	$(DRIVER) -t trace41.txt -s $(TSH) -a $(TSHARGS)
stest42:
	$(DRIVER) -t trace42.txt -s $(TSH) -a $(TSHARGS)

# Run the tests using the reference shell program
rtest01:
	$(DRIVER) -t trace01.txt -s $(TSHREF) -a $(TSHARGS)
rtest02:
	$(DRIVER) -t trace02.txt -s $(TSHREF) -a $(TSHARGS)
rtest03:
	$(DRIVER) -t trace03.txt -s $(TSHREF) -a $(TSHARGS)
rtest34:
	$(DRIVER) -t trace34.txt -s $(TSHREF) -a $(TSHARGS)
rtest35:
	$(DRIVER) -t trace35.txt -s $(TSHREF) -a $(TSHARGS)
rtest36:
	$(DRIVER) -t trace36.txt -s $(TSHREF) -a $(TSHARGS)
rtest37:
	$(DRIVER) -t trace37.txt -s $(TSHREF) -a $(TSHARGS)
rtest38:
	$(DRIVER) -t trace38.txt -s $(TSHREF) -a $(TSHARGS)
rtest39:
	$(DRIVER) -t trace39.txt -s $(TSHREF) -a $(TSHARGS)
rtest40:
	$(DRIVER) -t trace40.txt -s $(TSHREF) -a $(TSHARGS)
rtest41:
	$(DRIVER) -t trace41.txt -s $(TSHREF) -a $(TSHARGS)
rtest42:
	$(DRIVER) -t trace42.txt -s $(TSHREF) -a $(TSHARGS)


# clean up
clean:
	rm -f $(FILES) *.o *~
