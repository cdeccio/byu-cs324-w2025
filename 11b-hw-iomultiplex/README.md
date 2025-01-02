# I/O Multiplexing

The purpose of this assignment is to give you hands-on experience with
I/O multiplexing.  Code is provided for an echo server that listens for clients
to connect over a TCP connection (socket of type `SOCK_STREAM`) and echoes back
their messages, one line at a time, until they disconnect.  The server is
single-threaded and uses I/O multiplexing with epoll.  You will change it to
use nonblocking sockets, and edge-triggered monitoring to extra efficiency.


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

    - Sections 12.1 - 12.2 in the book
    - `epoll (7)` - general overview of epoll, including detailed examples

    Additionally, man pages for the following are referenced throughout the
    assignment:

    - `epoll_create1(2)` - shows the usage of the simple function to create an
      epoll instance
    - `epoll_ctl(2)` - shows the definition of the `epoll_data_t` and
      `struct epoll_event` structures, which are used by both `epoll_ctl()` and
      `epoll_wait()`.  Also describes the event types with which events are
      registered to an epoll instance, e.g., for reading or writing, and which
      type of triggering is used.
    - `epoll_wait()` - shows the usage of the simple `epoll_wait()` function,
      including how events are returned and how errors are indicated.
    - `fcntl(2)` - used to make sockets nonblocking
    - `recv(2)`, `read(2)`

 2. Run `make` to build the server `echoservere`.

 3. Start a tmux session with four panes open.  You are welcome to arrange them
    however you want, but it might be easiest to do it something like this:

    ```
    -------------------------------------
    |   client 1    |      client 2     |
    -------------------------------------
    |             server                |
    -------------------------------------
    |            analysis               |
    -------------------------------------
    ```


# I/O Multiplexing with Epoll

First, please note the following major sections to `echoservere.c`:

 - Server socket setup.  This is the code that prepares (1) the listening
   socket, i.e., the one with which new client connections will be accepted
   with `accept()`, and (2) the epoll instance, which will be used to register
   file descriptors for events.
 - Main event loop.  This is the loop that repeatedly calls `epoll_wait()` and
   then handles the event(s) that triggered `epoll_wait()` to return.  Within
   this loop are two main sections:
   - Handle new clients.  This code is run when an event is associated with
     the listen socket, which means that a new connection has been made, and
     `accept()` can be called on the listen socket.  After `accept()` has been
     called, the file descriptor associated with the newly-created socket is
     registered with the epoll instance.

     Note that the listening socket has already been set to use nonblocking
     I/O and edge-triggered monitoring.  That simply means that when an event
     is triggered for the file descriptor associated with the listening
     socket, `accept()` must be called repeatedly until there are no more
     incoming client connections pending.  More on this later.
   - Handle existing clients.  This code is run when an event is associated
     with a file descriptor other than that listen socket, i.e., one that goes
     with one of the existing clients.  In this case, `recv()` is called to
     read from the socket, after which `send()` is called to return the bytes
     read back to the client over the same socket.

Now start the `echoservere` server in the "server" pane using the following
command line:

(Replace "port" with a port of your choosing, an integer between 1024 and
65535.  Use of ports with values less than 1024 require root privileges).

```bash
./echoservere port
```

In each of the two "client" panes run the following:

(Replace "port" with the port on which the server program is now listening.)

```bash
nc localhost port
```

"localhost" is a domain name that always refers to the local system.  This is
used in the case where client and server are running on the same system.

After both are running, type some text in the first of the two "client" panes,
and press enter.  Repeat with the second "client" pane.  In the "analysis" pane
run the following:

```bash
ps -Lo user,pid,ppid,nlwp,lwp,state,ucmd -C echoservere | grep ^$(whoami)\\\|USER
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

Stop each of the clients and then the server by using `ctrl`+`c` in each of the
panes.


# Nonblocking Sockets

To illustrate the motivation for nonblocking sockets, modify `echoservere.c` by
surrounding the line containing the `epoll_wait()` statement with the following
two print statements:

```c
printf("before epoll_wait()\n"); fflush(stdout);
// epoll_wait() goes here...
printf("after epoll_wait()\n"); fflush(stdout);
```

Now change the value of the `len` argument passed to `recv()` in
`echoservere.c` from `MAXLINE` to `1`.

With these changes, the server is forced to read from the socket one byte at a
time.

Run `make` again, then start the server in the "server" pane:

(Replace "port" with a port of your choosing.)

```bash
./echoservere port
```

In one of the "client" panes run the following:

(Replace "port" with the port on which the server program is now listening.)

```bash
nc localhost port
```

Type "foo" in the "client" pane where `nc` is running.  Then press "Enter".
This sends four bytes to the server ("foo" plus newline).

 4. How many times did `epoll_wait()` return in conjunction with receiving the
    bytes sent by the client?  Do not include the event triggered by the
    incoming client connection, before data was sent.

The inefficiency here is that `epoll_wait()` was called more times than was
necessary.  Each time `recv()` was called in the loop, it could have been
called again to get more bytes that were available to be read.  However, the
concern with calling `recv()` repeatedly on a blocking socket is that when the
data has all been read, the call to `recv()` blocks.  That is where nonblocking
sockets come in.

To make the sockets nonblocking, uncomment all the commented code in
`echoservere.c` that starts with "UNCOMMENT FOR NONBLOCKING".  These changes
can be described as follows:

 - The `fcntl()` system call sets the socket corresponding to the newly
   connected client connection (`connfd`) to nonblocking.  The `fcntl()`
   statement might be read as follows: "set the flags on the socket associated
   with `connfd` to whatever flags are currently set plus the nonblocking flag
   (`O_NONBLOCK`)".

 - The `while(1)` loop in the `else` statement (opposite the conditional
   `if (sfd == active_client->fd)`)
   indicates the program repeated call `recv()` on the now-nonblocking socket
   until (1) the client has closed its end of the connection; (2) there is no
   more data left to read at the moment ; or (3) there is an error (indicated
   by `recv()` returning a value less than 0).  For each of these cases, there
   is a `break` statement to uncomment.

Run `make` again, then start the server in the "server" pane:

(Replace "port" with a port of your choosing.)

```bash
./echoservere port
```

In one of the "client" panes run the following:

(Replace "port" with a port of your choosing.)

```bash
nc localhost port
```
Type "foo" in the "client" pane where `nc` is running.  Then press "Enter".
This sends four bytes to the server ("foo" plus newline).

Answer the following questions about the epoll-based concurrency.  Use the man
pages for `read(2)` and `recv(2)`, the `echoservere.c` code, and the output of
both `echoservere` and `nc` to help you answer.

 5. How many times did `epoll_wait()` return in conjunction with receiving the
    bytes sent by the client?  Do not include the event triggered by the
    incoming client connection, before data was sent.

 6. What does it mean when `read()` or `recv()` returns a value greater than 0
    on a blocking or nonblocking socket?

 7. What does it mean when `read()` or `recv()` returns 0 on a blocking or
    nonblocking socket?

 8. What does it mean when `read()` or `recv()` returns a value less than 0 on
    a blocking socket?

 9. Why should `errno` be checked when `read()` or `recv()` returns a value
    less than 0 on a nonblocking socket?

 10. Which values of `errno` have a special meaning for nonblocking sockets when
     `read()` or `recv()` returns a value less than 0?

Stop the client and then the server by using `ctrl`+`c` in their respective
panes.


# Edge-Triggered Monitoring

Edge-triggered monitoring with epoll replaces the default behavior of
level-triggered monitoring. With level-triggered monitoring, `epoll_wait()`
returns for an event if the data is ready and has not been read.  With
edge-triggered monitoring, `epoll_wait()` only returns for an event if the data
is _new_.  Edge-triggered monitoring gives us minimal notification, which
increases efficiency.

To illustrate how this works, modify `echoservere.c` in the following ways:

 - Add a `break` statement immediately before the closing curly bracy (`}`) of
   the `while()` loop that repeatedly calls `recv()` on the socket associated
   with an existing client.

   This is a bit silly, but it is simply a way to temporarily remove the
   effects of the `while()` loop without changing a bunch of code that we'll
   need later.  After adding the  changes, the code in the `while()` loop will
   always be run exactly once, as if the loop wasn't a loop at all.

 - Modify the events for which a new client file descriptor (`connfd`) is
   registered by adding `EPOLLET` to the `events` member of the `struct
   epoll_event` used with `epoll_ctl()` to register it:

   ```c
   event.events = EPOLLIN | EPOLLET;
   ```

Run `make` again, then start the server in the "server" pane:

(Replace "port" with a port of your choosing.)

```bash
./echoservere port
```

In one of the "client" panes run the following:

(Replace "port" with the port on which the server program is now listening.)

```bash
nc localhost port
```

Type "foo" in the "client" pane where `nc` is running.  Then press "Enter".
This sends four bytes to the server ("foo" plus newline).

Answer the following questions about the epoll-based concurrency.  Use the man
pages for `epoll(7)`, the `echoservere.c` code, and the output of both
`echoservere` and `nc` to help you answer.

 11. How many times did `epoll_wait()` return in conjunction with receiving the
     bytes sent by the client?  Do not include the event triggered by the
     incoming client connection, before data was sent.

 12. How many total bytes have been read from the socket and echoed back to the
     client at this point?

Type "bar" in the "client" pane where `nc` is running.  Then press "Enter".
This sends four additional bytes to the server ("bar" plus newline).

 13. What happened to the bytes from "foo" that had been _received_ by the
     kernel but not yet _read_ from the socket?

 14. Why did `epoll_wait()` not return even though there was data to be read?

Stop the client and then the server by using `ctrl`+`c` in their respective
panes.

Remove the `break;` statement at the end of the `while(1)` loop (i.e., the one
you inserted at the beginning of this section).

Run `make` again, then start the server in the "server" pane:

(Replace "port" with a port of your choosing.)

```bash
./echoservere port
```

In one of the "client" panes run the following:

(Replace "port" with the port on which the server program is now listening.)

```bash
nc localhost port
```

Type "foo" in the "client" pane where `nc` is running.  Then press "Enter".
This sends four bytes to the server ("foo" plus newline).

You should now observe the behavior of an efficient, concurrent echo server
that uses I/O multiplexing with epoll, nonblocking sockets, and edge-triggered
monitoring!  Note that the server socket used for accepting new connections was
already set up to use nonblocking sockets and edge-triggered monitoring; you
simply added this behavior to the sockets corresponding to incoming client
connections as well.

Finally, revert the value in `recv()` back to `MAXLINE` from `1`.  You now
have model code to use in other projects that use epoll!
