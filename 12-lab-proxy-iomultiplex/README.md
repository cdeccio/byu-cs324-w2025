# HTTP Proxy Lab - I/O Multiplexing

The purpose of this assignment is to help you become more familiar with the
concepts associated with client and server sockets that are nonblocking, as
part of the I/O multiplexing concurrency paradigm.  You will learn these
concepts by building a working HTTP proxy that uses epoll.


# Maintain Your Repository

 Before beginning:
 - [Mirror the class repository](../01a-hw-private-repo-mirror), if you haven't
   already.
 - [Merge upstream changes](../01a-hw-private-repo-mirror#update-your-mirrored-repository-from-the-upstream)
   into your private repository.

 As you complete the assignment:
 - [Commit changes to your private repository](../01a-hw-private-repo-mirror#commit-and-push-local-changes-to-your-private-repo).


# Table of Contents

 - [Overview](#overview)
 - [Preparation](#preparation)
   - [Reading](#reading)
 - [Instructions](#instructions)
   - [Part 1 - HTTP Request Parsing](#part-1---http-request-parsing)
     - [Checkpoint 1](#checkpoint-1)
   - [Part 2 - Client Request Data and Client Request States](#part-2---client-request-data-and-client-request-states)
   - [Part 3 - I/O Multiplexing HTTP Proxy](#part-3---io-multiplexing-http-proxy)
     - [Handling a New HTTP Client](#handling-a-new-http-client)
     - [Checkpoint 2](#checkpoint-2)
     - [Receiving the HTTP Request](#receiving-the-http-request)
     - [Checkpoint 3](#checkpoint-3)
     - [Sending the HTTP Request](#sending-the-http-request)
     - [Checkpoint 4](#checkpoint-4)
     - [Receiving the HTTP Response](#receiving-the-http-response)
     - [Checkpoint 5](#checkpoint-5)
     - [Returning the HTTP Response](#returning-the-http-response)
     - [Testing](#testing)
 - [Additional Resources](#additional-resources)
   - [Non-Blocking I/O](#nonblocking-io)
 - [Testing](#testing-1)
   - [Manual Testing - Non-Local Server](#manual-testing---non-local-server)
   - [Manual Testing - Local Server](#manual-testing---local-server)
   - [Automated Testing](#automated-testing)
 - [Debugging Hints](#debugging-hints)
 - [Evaluation](#evaluation)
 - [Submission](#submission)


# Overview

In this lab, you will be implementing an HTTP proxy that handles
concurrent requests.  However, unlike the HTTP proxy implemented in the
[HTTP Proxy with Threadpool Lab](../10-lab-proxy-threadpool),
the HTTP proxy you produce will achieve concurrency using I/O multiplexing.
Your server will not spawn any additional threads or processes (i.e., it will
be single-threaded), and all sockets will be set to nonblocking.  While your
server will not take advantage of multiprocessing, it will be more efficient by
holding the processor longer because it is not blocking (and thus sleeping) on
I/O.  This model is also referred to as an example of *event-based* programming,
wherein execution of code is dependent on "events"--in this case the
availability of I/O.


# Preparation

## Reading

Read the following in preparation for this assignment:

 - Sections 11.1 - 11.6, 12.1 - 12.2 in the book
 - `epoll (7)` - general overview of epoll, including detailed examples

Additionally, man pages for the following are referenced throughout the
assignment:

 - `epoll_create1(2)` - shows the usage of the simple function to create an
   epoll instance
 - `epoll_ctl(2)` - shows the definition of the `epoll_data_t` and
   `struct epoll_event` structures, which are used by both `epoll_ctl()` and
   `epoll_wait()`.  Also describes the event types with which events are
   registered to an epoll instance, e.g., for reading or writing, and which
   type of triggering is used (for this lab you will use edge-triggered
   monitoring).
 - `epoll_wait()` - shows the usage of the simple `epoll_wait()` function,
   including how events are returned and how errors are indicated,
 - `fcntl(2)` - used to make sockets nonblocking
 - `socket(2)`, `socket(7)`
 - `send(2)`
 - `recv(2)`
 - `bind(2)`
 - `connect(2)`
 - `getaddrinfo(3)`


# Instructions

## Part 1 - HTTP Request Parsing

Follow the instructions for implementing HTTP request parsing from
[HTTP Proxy Lab - Threadpool Lab](../10-lab-proxy-threadpool#part-1---http-request-parsing),
if you haven't already.

### Checkpoint 1

Refer to [Checkpoint 1](../10-lab-proxy-threadpool#checkpoint-1) in the
threadpool lab.


## Part 2 - Client Request Data and Client Request States

### Client Request Data

Define a `struct request_info` to keep track of data associated with handling
each request.  The following paragraphs explain why this is necessary and
provide a sample list of data members that you might include in such a request.

The reason for defining a single structure for keeping track of data associated
with a given request is that, just like when using blocking sockets, you won't
always be able to receive or send all your data with a single call to `read()`
or `write()`.  With blocking sockets in a multi-threaded server, the solution
was to use a loop that received or sent until you had everything, before you
moved on to anything else.  Because the sockets were configured as blocking,
the kernel would context switch out the thread and put it into a sleep state
until there was I/O.

However, with I/O multiplexing, you can't simply call `read()` repeatedly or it
would block the entire single-threaded process. Instead, you must stop when
there is no more data to read and move on to handling the other ready events.
Because you are handling all HTTP requests with a single thread, you don't have
the ease of declaring variables associated with handling a given HTTP request
on that thread's stack.  Sharing those variables across multiple concurrent
client requests would really mess things up!

You can avoid this by defining a struct to keep track of all the state
associated with handling a given HTTP request.  When a new client connection is
accepted, then a new instance of this struct is allocated and initialized for
the new HTTP request.  This instance is registered with the file descriptor
associated with the new client connection using `epoll_ctl()`.  The `data.ptr`
member of the `struct epoll_event` used with `epoll_ctl()` points to the newly
allocated and initialized allocated struct.  Now when there is an event, your
code uses the `data.ptr` member of the event returned to retrieve that
instance.  This is how the code knows where it left off and thus where to pick
up this time.  Here is a list of members that that structure might contain.
Note that these should loosely correspond to local variables used in the
[thread- or threadpool-based version of the proxy](../10-lab-proxy-threadpool).

 - the client-to-proxy socket, i.e., the one corresponding to the requesting
   client
 - the proxy-to-server socket, i.e., the one corresponding to the connection
   to the HTTP server
 - the current state of the request (see note below).
 - the buffer(s) to read into and write from
 - the total number of bytes read from the client
 - the total number of bytes to write to the server
 - the total number of bytes written to the server
 - the total number of bytes read from the server
 - the total number of bytes written to the client


### Client Request States

A note about the "current state" member above.  Because handling an HTTP
request involves various tasks (e.g., receive request from client, send request
to server, etc.), it is helpful to think about the problem in terms of "states"
with events that trigger transitions between these states.  It is recommended
that you use the following set of request states, each associated with
different I/O operations related to HTTP proxy operation:

 - `READ_REQUEST`
 - `SEND_REQUEST`
 - `READ_RESPONSE`
 - `SEND_RESPONSE`

These could be defined in one of several ways.  One way is to use:

```c
#define READ_REQUEST 1
#define SEND_REQUEST 2
#define READ_RESPONSE 3
#define SEND_RESPONSE 4
```

There is not an easy way to test this until the next part, when you populate
your `struct request_info` with actual information associated with an incoming
HTTP request.


## Part 3 - I/O Multiplexing HTTP Proxy

As you implement this section, you might find it helpful to refer to the TCP
code from the
[sockets homework assignment](../07-hw-sockets)
the
[I/O multiplexing homework assignment](../11b-hw-iomultiplex),
and the
[HTTP proxy with threadpool lab](../10-lab-proxy-threadpool).


### Handling a New HTTP Client

Write functions for each of the following:

 - `open_sfd()` - Create and configure a TCP socket for listening and accepting
   new client connections.
   - Create a socket with address family `AF_INET` and type
     `SOCK_STREAM`.
   - Use the following command to set an option on the socket to
     allow it bind to an address and port already in use:

     ```c
     int optval = 1;
     setsockopt(sfd, SOL_SOCKET, SO_REUSEPORT, &optval, sizeof(optval));
     ```

     While this might seem like a bad idea, during development of your proxy
     server, it will allow you to immediately restart your HTTP proxy after
     failure, rather than having to wait for it to time out.
   - Configure the socket to use *nonblocking I/O* (see the
     [I/O Multiplexing assignment](../11b-hw-iomultiplex/)) for an example.
   - `bind()` it to a port passed as the first argument from the
     command line, and configure it for accepting new clients with `listen()`.
   - Return the file descriptor associated with the listening socket.
 
 - `handle_new_clients()` - Accept and prepare for communication with incoming
   clients.
   - Loop to `accept()` any and all client connections.  For each new file
     descriptor (i.e., corresponding to a new client) returned:
     - Configure it to use nonblocking I/O.  See the
       [I/O Multiplexing assignment](../11b-hw-iomultiplex/) for a full,
       working example.
     - Allocate memory for a new `struct request_info` and initialize the
       values in that `struct request_info`.  The initial state should be
       `READ_REQUEST`.
     - Using `epoll_ctl()` and `EPOLL_CTL_ADD`, register each returned
       client-to-proxy socket with the epoll instance that you created, for
       reading, using edge-triggered monitoring (i.e., `EPOLLIN | EPOLLET`).
       Associate the newly-allocated `struct request_info` with the event by
       assigning the `data.ptr` member to it.

     You should only break out of your loop and stop calling `accept()` when it
     returns a value less than 0, in which case:
     - If `errno` is set to `EAGAIN` or `EWOULDBLOCK`, then that is an
       indicator that there are no more clients currently pending;
     - If `errno` is anything else, this is an error.  Use `perror()` to print
       out the error description.

     Have your HTTP proxy print the newly created file descriptor associated with
     any new clients.  You can remove this later, but it will be good for you
     to see now that they are being created.

     You will need to pass your epoll file descriptor as an argument, so you
     can register the new file descriptor with the epoll instance.

Now add the following to `main()`:

 - Create an epoll instance with `epoll_create1()`.
 - Call `open_sfd()` to get your listening socket.
 - Register your listening socket with the epoll instance that you created, for
   *reading* and for edge-triggered monitoring (i.e., `EPOLLIN | EPOLLET`).
 - Create a `while(1)` loop that does the following:
   - Calls `epoll_wait()` loop with a timeout of 1 second.
   - If the result was an error (i.e., return value from `epoll_wait()` is less
     than 0), then handle the error appropriately (see the man page for
     `epoll_wait(2)` for more).
   - If there was no error, you should loop through all the events and handle
     each appropriately.  For now, just start with handling new clients.  We
     will implement the handling of existing clients later.  If the event
     corresponds to the listening file descriptor, then call
     `handle_new_clients()`.

At this point, your server is merely set up to listen for incoming client
connections and `accept()` them.  It is not yet doing anything else useful, but
you should be able to test your work so far!

Run the following to build your proxy:

```bash
make
```

Now use the following command to find a port that is unlikely to conflict with
that of another user:

```bash
./port-for-user.pl
```

Then run the following to start your HTTP proxy:

(Replace "port" with the port returned by `./port-for-user.pl`.)

```bash
./proxy port
```

Next you will use the `curl` command-line HTTP client to test your code.
`curl` is described more in the [HTTP homework assignment](../09a-hw-http).
For the purposes of this section, `curl` creates and sends an HTTP request to
your HTTP proxy, which is designated with `-x`.

The `./slow-client.py` script  acts like `curl`, but it spreads its HTTP
request over several calls to `send()` to test the robustness of your proxy
server in reading from a byte stream.  The `-b` option designates the amount of
time (in seconds) that it will sleep in between lines that it sends.

From another terminal on the same machine, run the following:

(NOTE: the commands below are expected to _fail_ at this point, in part because
your HTTP proxy implementation is incomplete.  The commands are merely a way
to see how your HTTP proxy behaves with its current, incomplete
functionality.  What is important is the proxy output, showing that you have
parsed things correctly.)

(Replace "port" with the port on which your HTTP proxy is listening.)

```bash
curl -x http://localhost:port/ "http://www-notls.imaal.byu.edu/cgi-bin/slowsend.cgi?obj=lyrics"
```


### Checkpoint 2

Your HTTP proxy should be printing the file descriptors associated with each
new client connection at this point.  However, you shouldn't expect it to be
doing much else--not just yet anyway.


### Receiving the HTTP Request

Write a function, `handle_client()`, that takes a pointer to a
[struct client request](#part-2---client-request-data-and-client-request-states).
The function should use the `struct client request` pointer passed in to
determine what state the request is currently in.

Then do the following:

 - When your client enters `handle_client()`, print out both the file
   descriptor associated with the client-to-proxy socket and the current state.
   This way you always know something about the request for which an event was
   recently triggered.

 - If in the `READ_REQUEST` state (other states will be addressed later), read
   from the client-to-proxy socket in a loop until one of the following
   happens:

   (Note that the request will not exceed 1024 bytes.)

   - the entire HTTP request has been read--that is, the request contains
     `\r\n\r\n`.  If this is the case:

     - Print out the HTTP request using `print_bytes()`.  This will allow you
       to see exactly what bytes were received.
     - Add a null-terminator to the HTTP request, and pass it to the
       `parse_request()` function, allowing it to extract the individual values
       associated with the request.
     - Print out the components of the HTTP request, once you have received it
       in its entirety (e.g., like `test_parser()` does).  This includes the
       method, hostname, port, and path.  Because these should all be
       null-terminated strings of type `char []`, you can use `printf()`.
     - Create the request that you will send to the server using the
       [instructions from the threadpool proxy lab](../10-lab-proxy-threadpool#creating-an-http-request).
     - Use `print_bytes()` to print out the HTTP request you created.
     - Create a new socket and call `connect()` to the HTTP server.
     - Configure the new socket as nonblocking. (Do this only _after_ calling
       `connect()`!)
     - Using `epoll_ctl()` and `EPOLL_CTL_DEL`, deregister the client-to-proxy
       socket with the epoll instance that you created.
     - Register the proxy-to-server socket with the epoll instance that you
       created, for _writing_ (i.e., `EPOLLOUT`).
     - Change the state of the request to `SEND_REQUEST`.

   - `read()` (or `recv()`) returns a value less than 0.
     - If `errno` is `EAGAIN` or `EWOULDBLOCK`, it just means that there is no
       more data ready to be read; you will continue reading from the socket
       when you are notified by epoll that there is more data to be read.
     - If `errno` is anything else, this is an error.  Print out the error with
       `perror()`, close the client-to-proxy socket, and free the memory
       associated with the current `struct request_info *`.  Closing the socket
       automatically deregisters it from any associations with the epoll
       instance.

   - At this point, you can return from the function.  There is no more that
     can be done with the current HTTP request at this time.  `epoll_wait()`
     will notify you when more can be done.

Now add some code to your `epoll_wait()` loop.  Cast the `data.ptr` member of the
`struct epoll_event` that represents the current event to a
`struct request_info *`.  Determine whether the `struct request_info` instance
referred to is the listening socket or corresponds to an existing client.  If
the listening socket, then call `handle_new_clients()`; otherwise, call
`handle_client()`.

Re-build and re-start your proxy, and make sure it works properly when you run
the following:

(NOTE: the commands below are still expected to fail.)

(Replace "port" with the port on which your HTTP proxy is listening.)

```bash
curl -x http://localhost:port/ "http://www-notls.imaal.byu.edu/cgi-bin/slowsend.cgi?obj=lyrics"
```
```bash
./slow-client.py -x http://localhost:port/ -b 1 "http://www-notls.imaal.byu.edu/cgi-bin/slowsend.cgi?obj=lyrics"
```

### Checkpoint 3

Use output from your print statements to verify that 1) your HTTP proxy has
received the entire HTTP request, 2) your HTTP proxy has properly extracted the
components of the HTTP request, and 3) the proxy-to-server HTTP request has been
appropriately created.  

Note that the `curl` command should result in a client request entering the
`handle_client()` function in the `READ_REQUEST` state only once, but the
`slow-client.py` command should require at least two times through the
`handle_client()` function in the `READ_REQUEST` state.  In both cases, your
HTTP proxy should eventually enter `handle_client()` in the `SEND_REQUEST`
because it has finished receiving and parsing the request.

Now would be a good time to save your work, if you haven't already.


### Sending the HTTP Request

Now that your proxy can read an HTTP request from a client and create an HTTP
request to be sent to the server, it is time to send the request, i.e., the
`SEND_REQUEST` state.  In the `handle_client()` function, add the following
functionality.

If in the `SEND_REQUEST` state, loop to write the request to the server
using the proxy-to-server socket until one of the following happens:

 - you have sent the entire HTTP request to the server.  If this is the case:
   - Deregister the proxy-to-server socket with the epoll instance for writing.
   - Register the proxy-to-server socket with the epoll instance for reading.
   - Change state to `READ_RESPONSE`.
 - `write()` (or `send()`) returns a value less than 0.
   - If `errno` is `EAGAIN` or `EWOULDBLOCK`, it just means that there is no
     buffer space available for writing to the socket; you will continue
     writing to the socket when you are notified by epoll that there is more
     buffer space available for writing.
   - If `errno` is anything else, this is an error.  Print out the error with
     `perror()`, close both client-to-proxy and proxy-to-server sockets, and
     free the memory associated with the current `struct request_info *`.
     Closing the sockets automatically deregisters your sockets from any
     associations with the epoll instance.

At this point, you can return from the function.  There is no more that can be
done with the current HTTP request at this time.  `epoll_wait()` will notify
you when more can be done.

Now would be a good time to test with the following commands:

(NOTE: the commands below are still expected to fail.)

(Replace "port" with the port on which your HTTP proxy is listening.)

```bash
curl -x http://localhost:port/ "http://www-notls.imaal.byu.edu/cgi-bin/slowsend.cgi?obj=lyrics"
```
```bash
./slow-client.py -x http://localhost:port/ -b 1 "http://www-notls.imaal.byu.edu/cgi-bin/slowsend.cgi?obj=lyrics"
```

### Checkpoint 4

In addition to what you were observing before, you should now observe your HTTP
proxy eventually entering `handle_client()` in the `READ_RESPONSE` state because
it has finished sending the request.

Now would be a good time to save your work, if you haven't already.


### Receiving the HTTP Response

Once your proxy has sent the HTTP request to the HTTP server, it is time to
read the response, i.e., the `READ_RESPONSE` state.  In the `handle_client()`
function, add the following functionality.

If in the `READ_RESPONSE` state, loop to read from the proxy-to-server socket
until one of the following happens:

 (Note that the size of the response will not exceed 16384 bytes.)

 - you have read the entire HTTP response from the server.  Since this is
   HTTP/1.0, this is when the call to `read()` (or `recv()`) returns 0,
   indicating that the server has closed the connection.  If this is the case:
   - Close the proxy-to-server socket.
   - Use `print_bytes()` to print out the HTTP response you received.
   - Register the client-to-proxy socket with the epoll instance for writing.
   - Change state to `SEND_RESPONSE`.
 - `read()` (or `recv()`) returns a value less than 0.
   - If `errno` is `EAGAIN` or `EWOULDBLOCK`, it just means that there is no
     more data ready to be read; you will continue reading from the socket when
     you are notified by epoll that there is more data to be read.
   - If `errno` is anything else, this is an error.  Print out the error with
     `perror()`, close both client-to-proxy and proxy-to-server sockets, and
     free the memory associated with the current `struct request_info *`.
     Closing the sockets automatically deregisters your sockets from any
     associations with the epoll instance.

At this point, you can return from the function.  There is no more that can be
done with the current HTTP request at this time.  `epoll_wait()` will notify
you when more can be done.

Now would be a good time to test with the following commands:

(NOTE: the commands below are still expected to fail.)

(Replace "port" with the port on which your HTTP proxy is listening.)

```bash
curl -x http://localhost:port/ "http://www-notls.imaal.byu.edu/cgi-bin/slowsend.cgi?obj=lyrics"
```
```bash
./slow-client.py -x http://localhost:port/ -b 1 "http://www-notls.imaal.byu.edu/cgi-bin/slowsend.cgi?obj=lyrics"
```


### Checkpoint 5

Use output from your print statements to verify that your HTTP proxy has
received the entire HTTP response.  Note that the requests for
`/cgi-bin/slowsend.cgi`  command should result in a client request entering the
`handle_client()` function in the `READ_RESPONSE` state at least two times.
Also, your HTTP proxy should eventually enter `handle_client()` in the
`SEND_RESPONSE` state because it has finished receiving the response.

Now would be a good time to save your work, if you haven't already.


### Returning the HTTP Response

Once your proxy has received the HTTP response from the HTTP server, it is time
to send it back to the client, i.e., the `SEND_RESPONSE` state.  In the
`handle_client()` function, add the following functionality.

If in the `SEND_RESPONSE` state, loop to write the response to the server
using the client-to-proxy socket until one of the following happens:

 - you have written the entire HTTP response to the client socket.  If this is
   the case:
   - Free the memory associated with the current `struct request_info *`.
   - Close your client-to-proxy socket.
   - You are done!
 - `write()` (or `send()`) returns a value less than 0.
   - If `errno` is `EAGAIN` or `EWOULDBLOCK`, it just means that there is
     no buffer space available for writing to the socket; you will continue
     writing to the socket when you are notified by epoll that there is more
     buffer space available for writing.
   - If `errno` is anything else, this is an error.  Print out the error with
     `perror()`, close the client-to-proxy socket, and free the memory
     associated with the current `struct request_info *`.  Closing the socket
     automatically deregisters it from any associations with the epoll
     instance.

At this point, you can return from the function.  The HTTP request has been
successfully handled!

Now would be a good time to test with the following commands:

(NOTE: the commands below are still expected to fail.)

(Replace "port" with the port on which your HTTP proxy is listening.)

```bash
curl -x http://localhost:port/ "http://www-notls.imaal.byu.edu/cgi-bin/slowsend.cgi?obj=lyrics"
```
```bash
./slow-client.py -x http://localhost:port/ -b 1 "http://www-notls.imaal.byu.edu/cgi-bin/slowsend.cgi?obj=lyrics"
```


### Testing

At this point you should be able to pass:
 - [Tests performed against a non-local HTTP server](#manual-testing---non-local-server).
 - [Tests performed against a local HTTP server](#manual-testing---local-server).
 - [Automated tests](#automated-testing) with the following command:
   ```bash
   ./driver.py -b 60 -c 35 epoll
   ```


# Additional Resources

## Non-Blocking I/O

All sockets that your proxy will use should be set up for nonblocking I/O.
This includes the listen socket, the sockets associated with communications
between client and proxy, and the sockets associated with communications
between proxy and server.

Additionally, all sockets must be registered with the epoll instance--for
reading or writing--using edge-triggered monitoring.

That being said, for simplicity, you _should_ wait to set the proxy-to-server
socket as nonblocking _after_ you call `connect()`, rather than before.  While
that will mean that your server not fully nonblocking, it will allow you to
focus on the more important parts of I/O multiplexing.  This is permissible.

If you choose to ignore the previous paragraph and set the proxy-to-server
socket as nonblocking before calling `connect()`, you can execute `connect()`
immediately, but you cannot initiate the `write()` call until `epoll_wait()`
indicates that this socket is ready for writing. Because the socket is
nonblocking, `connect()` will return before the connection is actually
established.  In this case, the return value is -1 and `errno` is set to
`EINPROGRESS` (see the `connect(2)` man page).  This also means that when
iterating through the results of `getaddrinfo()` when a socket is nonblocking,
the return value of `connect()` is not a useful check for determining whether a
given address is reachable.


# Testing

Some tools are provided for testing--both manual and automated:

 - A python-based HTTP server
 - A driver for automated testing


## Manual Testing - Non-Local Server

See
[Manual Testing - Non-Local Server](../10-lab-proxy-threadpool#manual-testing---non-local-server).


## Manual Testing - Local Server

See
[Manual Testing - Local Server](../10-lab-proxy-threadpool#manual-testing---local-server).


## Automated Testing

See
[Automated Testing](../10-lab-proxy-threadpool#automated-testing),
but use "epoll" in place of "threadpool" whenever the driver is used.


# Debugging Hints

See
[Debugging Hints](../10-lab-proxy-threadpool#debugging-hints).


# Evaluation

Your score will be computed out of a maximum of 100 points based on the
following distribution:

 - 60 for basic HTTP proxy functionality with epoll
 - 35 for handling concurrent HTTP proxy requests using epoll
 - 5 - compiles without any warnings

Run the following to check your implementation:

```b
./driver.py -b 60 -c 35 epoll
```


# Submission

Upload `proxy.c` to the assignment page on LearningSuite.
