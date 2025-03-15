# Concurrency

The purpose of this assignment is to give you hands-on experience with
concurrency.  Code is provided for an echo server that listens for clients to
connect over a TCP connection (socket of type `SOCK_STREAM`) and echoes back
their messages, one line at a time, until they disconnect.  You will experiment
with that code and analyze what it is doing.


# Maintain Your Repository

 Before beginning:
 - [Mirror the class repository](../01a-hw-private-repo-mirror), if you haven't
   already.
 - [Merge upstream changes](../01a-hw-private-repo-mirror#update-your-mirrored-repository-from-the-upstream)
   into your private repository.

 As you complete the assignment:
 - [Commit changes to your private repository](../01a-hw-private-repo-mirror#commit-and-push-local-changes-to-your-private-repo).


# Preparation

 1. Read the following in preparation for this assignment:

    - Sections 12.1 and 12.3 - 12.5 in the book

    Additionally, man pages for the following are also referenced throughout the
    assignment:

    - `pthreads(7)`
    - `sem_init(3)`
    - `sem_wait(3)`
    - `sem_post(3)`

 2. Run `make` to build four servers: `echoserveri`, `echoserverp`,
    `echoservert`, and `echoservert_pre`.  These are versions of the echo
    server that use, respectively, no concurrency, process-based (using
    `fork()`) concurrency, simple thread-based concurrency (threads created on
    the fly), and thread-based concurrency using a thread-pool.

 3. Start a tmux session with five panes open.  You are welcome to arrange them
    however you want, but it might be easiest to do it something like this:

    ```
    -------------------------------------
    | client 1  | client 2  | client 3  |
    -------------------------------------
    |             server                |
    -------------------------------------
    |            analysis               |
    -------------------------------------
    ```


# Part 1: No Concurrency

Start the `echoserveri` server in the "server" pane using the following command line:

(Replace "port" with a port of your choosing, an integer between 1024 and
65535.  Use of ports with values less than 1023 require root privileges).

```bash
./echoserveri port
```

In each of the three "client" panes run the following:

(Replace "port" with the port on which the server program is now listening.)

```bash
nc localhost port
```

"localhost" is a domain name that always refers to the local system.  This is
used in the case where client and server are running on the same system.

After all three are running, type some text in the first of the three "client"
panes, and press enter.  Repeat with the second and third "client" panes, _in
that order_.  In the "analysis" pane run the following:

```bash
ps -Lo user,pid,ppid,nlwp,lwp,state,ucmd -C echoserveri | grep ^$(whoami)\\\|USER
```

The `ps` command lists information about processes that currently exist on the
system.  The `-L` option tells us to show threads ("lightweight processes") as
if they were processes.  The `-o` option is used to show only the following
fields:

 - user: the username of the user running the process
 - pid: the process ID of the process
 - ppid: the process ID of the parent process
 - nlwp: the number of threads (light-weight processes) being run
 - lwp: the thread ID of the thread
 - state: the state of the process, e.g., Running, Sleep, Zombie
 - ucmd: the command executed.

While some past homework assignments required you to use the `ps` command without
a pipeline (e.g., to send its output grep), `ps` has the shortcoming that it
can't simultaneously filter by both command name and user, so the above command
line is a workaround.

 1. Show the output from the `ps` command.

 2. From the `ps` output, how many (unique) processes are running and why?
    Use the PID and LWP to identify different threads or processes.

 3. From the `ps` output, how many (unique) threads are running with each
    process and why?  Use the PID and LWP to identify different threads or
    processes.

 4. Enter `Ctrl`+`c` on the pane in which `nc` was first executed to interrupt
    it.  *What happens to the `nc` processes in the other windows and why?*

Stop the server by using `ctrl`+`c` in the appropriate pane.


# Part 2: Process-based Concurrency

Repeat the exercises from Part 1 (except question 4), replacing all instances
of `echoserveri` with `echoserverp`, including in the `ps` command.  Answer
questions 1 through 3 for `echoserverp` as questions 5 through 7.


# Part 3: Simple Thread-based Concurrency

Repeat the exercises from Part 1 (except question 4), replacing all instances
of `echoserveri` with `echoservert`, including in the `ps` command.  Answer
questions 1 through 3 for `echoservert` as questions 8 through 10.


# Part 4: Threadpool-based Concurrency

Repeat the exercises from Part 1 (except question 4), replacing all instances
of `echoserveri` with `echoservert_pre`, including in the `ps` command.  Answer
questions 1 through 3 for `echoservert_pre` as questions 11 through 13.


# Part 5: Producer-Consumer Review

Modify `echoservert_pre.c` by sandwiching the line containing the `accept()`
statement between the following two print statements:

```c
printf("before accept()\n"); fflush(stdout);
// accept() goes here...
printf("after accept()\n"); fflush(stdout);              
```

Open `sbuf.c` (in the `../code` directory), and put similar `printf()` statements
around the following lines:
 - `sem_wait(&sp->slots);`
 - `sem_post(&sp->items);`
 - `sem_wait(&sp->items);`
 - `sem_post(&sp->slots);`

(You will need to add `#include <stdio.h>`.)

Run `make` again, then start the server in the "server" pane:

(Replace "port" with a port of your choosing.)

```bash
./echoservert_pre port
```

Use the output and the code itself to answer the following questions.

 14. How many producer threads are running?

 15. How many consumer threads are running?

 16. What is/are the producer thread(s) waiting on?

 17. What is/are the consumer thread(s) waiting on?

In one of the "client" panes run the following:

(Replace "port" with the port on which the server program is now listening.)

```bash
nc localhost port
```

 18. What event changes the state of the producer (i.e., so it is no longer
     waiting)?

 19. What event changes the state of the consumer(s)?

 20. How many consumers change state?

 21. What is the producer thread now waiting on?


Answer the following questions, considering the three concurrency models
examined in this assignment: processed-based (`echoserverp`); thread-based with
spawning threads on-the-fly (`echoservert`); and threadpool-based
(`echoservert_pre`).  You may use your own observations and/or refer to the book
(e.g., section 12.1.2).


 22. Which of the concurrency models has the most expensive _run-time_ cost for
     handling a given client and why?  Consider only the cost at the time new
     clients connect and are handled, and ignore any cost associated with
     server start-up.

 23. Which of the concurrency models has the most expensive _start-up_ cost and
     why?  Consider only the cost associated with server start-up, and ignore
     any cost at the time new clients connect and are handled.

 24. Which (one or more) of the three concurrency models, as implemented in
     this assignment, has/have an explicit limitation in terms of number of
     clients that can be handled concurrently and why?  Assume that system
     resources are unlimited.

 25. Which (one or more) of the three of the models allow(s) allow sharing of
     memory and data structures without the use of inter-process communication
     (e.g., pipes, sockets) and why?
