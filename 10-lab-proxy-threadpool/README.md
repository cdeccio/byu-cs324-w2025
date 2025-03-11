# HTTP Proxy Lab - Threadpool

The purpose of this assignment is to help you become more familiar with the
concepts associated with client and server sockets, HTTP, and concurrent
programming by building a working HTTP proxy server with a threadpool.


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
     - [`complete_request_received`](#complete_request_received)
     - [`parse_request`](#parse_request)
     - [Checkpoint 1](#checkpoint-1)
   - [Part 2 - Sequential HTTP Proxy](#part-2---sequential-http-proxy)
     - [Receiving the HTTP Request](#receiving-the-http-request)
     - [Checkpoint 2](#checkpoint-2)
     - [Creating an HTTP Request](#creating-an-http-request)
     - [Checkpoint 3](#checkpoint-3)
     - [Communicating with the HTTP Server](#communicating-with-the-http-server)
     - [Checkpoint 4](#checkpoint-4)
     - [Returning the HTTP Response](#returning-the-http-response)
     - [Checkpoint 5](#checkpoint-5)
   - [Part 3 - Threaded HTTP Proxy](#part-3---threaded-http-proxy)
     - [Checkpoint 6](#checkpoint-6)
   - [Part 4 - Threadpool](#part-4---threadpool)
     - [Checkpoint 7](#checkpoint-7)
 - [Testing](#testing-4)
   - [Manual Testing - Non-Local Server](#manual-testing---non-local-server)
   - [Manual Testing - Local Server](#manual-testing---local-server)
   - [Automated Testing](#automated-testing)
 - [Debugging Hints](#debugging-hints)
 - [Evaluation](#evaluation)
 - [Submission](#submission)


# Overview

An HTTP proxy is a program that acts as a intermediary between an HTTP client
(i.e., a Web browser) and an HTTP server.  Instead of requesting a resource
directly from the HTTP server, the HTTP client contacts the HTTP proxy,
which forwards the request on to the HTTP server. When the HTTP server replies
to the proxy, the proxy sends the reply on to the browser.  In this way, the
client acts as both a *server* (to the Web browser) and a *client* (to the HTTP
server).

Proxies are useful for many purposes.  Sometimes proxies are used in firewalls,
so that browsers behind a firewall can only contact a server beyond the
firewall via the proxy.  Proxies can also act as anonymizers: by stripping
requests of all identifying information, a proxy can make the browser anonymous
to HTTP servers.  Proxies can even be used to cache web objects by storing
local copies of objects from servers then responding to future requests by
reading them out of its cache rather than by communicating again with remote
servers.

In this lab, you will write a simple HTTP proxy objects.  For the first part of
the lab, you will set up the proxy to accept incoming connections, read and
parse requests, forward requests to web servers, read the servers' responses,
and forward those responses to the corresponding clients.  This first part will
involve learning about basic HTTP operation and how to use sockets to write
programs that communicate over network connections.  In the second part, you
will upgrade your proxy to deal with multiple concurrent connections using a
simple, thread-based model.  This will introduce you to dealing with
concurrency, a crucial systems concept.  In the the third part, you will modify
your concurrency approach to use a threadpool.


# Preparation

## Reading

Read the following in preparation for this assignment:

  - Sections 11.1 - 11.6, 12.1, and 12.3 - 12.5 in the book

Additionally, man pages for the following are referenced throughout the
assignment:

 - `tcp(7)`
 - `socket(2)`, `socket(7)`
 - `send(2)`
 - `recv(2)`
 - `bind(2)`
 - `connect(2)`
 - `getaddrinfo(3)`
 - `pthread_create(3)`
 - `pthread_detach(3)`
 - `pthread_self(3)`
 - `sem_init(3)`
 - `sem_post(3)`
 - `sem_wait(3)`
 - `sem_overview(7)` (unnamed semaphores)


# Instructions

## Part 1 - HTTP Request Parsing

The first step in building an HTTP proxy is parsing an incoming HTTP
request.  Some skeleton functions have been created for you in `proxy.c`,
namely `complete_request_received()` and `parse_request()`.  These are provided
in the case they are helpful for you, but you not are required to use them; if
it is more intuitive for you to complete this in another way, you are welcome
to do that.

These functions will be used by your HTTP proxy to know when a client is done
sending its request and to parse the request.


### `complete_request_received()`

`complete_request_received()` takes the following as an argument:
 - `char *request`: a (null-terminated) string containing an HTTP request.

This function tests whether or not the HTTP request associated with `request`
is complete.  In this lab, all requests will consist of only first line and one
or more HTTP headers; there will be no request body.  Thus, this function
should simply be checking for the end-of-headers sequence, `"\r\n\r\n"`.  It
returns 1 if that sequence is found (i.e., the request is complete) and 0
otherwise.  It is recommended that you use `strstr()` to check for the presence
of this value.


### `parse_request()`

Important note. For this part of the lab only (i.e., the creation of
`parse_request()`), you _may_ use a large language model (LLM), such as ChatGPT
or CodePilot, to generate code.  However, this is not required.  If you choose
to generate code with an LLM, you must meet the following requirements:
 - You are responsible for generating the appropriate prompts and making the
   appropriate modifications to LLM-generated code to make it work properly.
 - You are responsible for understanding the code and the concepts underlying
   it.
 - Your code _must_ use the function definition for `parse_request()` described
   below.
 - You _must_ include the following in the comments above the LLM-generated
   code:
   - The LLM used.
   - The prompt you provided in the comments above.
   - A brief description of what changes you had to make, if any, to get it to
     work properly.

`parse_request()` parses the complete HTTP request and stores the components in
strings that can be used to modify the request and issue it to the HTTP server.
The function takes the following as arguments:

 - `char *request`: a (null-terminated) string containing an HTTP request.
 - `char *method`: a string to which the method, extracted from the request, is
   copied.
 - `char *hostname`: a string to which the hostname, extracted from the URL, is
   copied.
 - `char *port`: a string to which the port, extracted from the URL, is
   copied.  If no port is specified in the URL, then it should be populated
   with "80", the default port for HTTP.
 - `char *path`: a string to which the path, extracted from the URL, is
   copied.  The path should include not only the file path, but also the query
   string, if any.

Your `parse_request()` method does not have to support every possible use case.
For the purposes of this lab, URLs will be well-formed.  You can use the
following simplified rules:

 - For an HTTP request:
   - All characters from the beginning of the string up to (but not including)
     the first space comprise the _request method_.
   - All characters between the first space and the second space
     (non-inclusive) comprise the _URL_.
   - All characters after the first line (i.e., after the first `\r\n`
     sequence) comprise the _headers_.  You do not need to further parse the
     headers.

 - For the URL extracted from the HTTP request:
   - If there is a colon `:` in the URL _after_ the `://`, then:
     - the digits immediately following the colon, up until the slash (`/`),
       non-inclusive, comprise the _port_;
     - characters between the `://` and the colon (non-inclusive) comprise the
       _hostname_; and
     - all characters after the port (including the first slash) comprise the
       _path_.
   - Otherwise:
     - the _port_ is 80 (the default);
     - characters between the `://` and the next slash (`/`), non-inclusive,
       comprise the _hostname_; and
     - all characters after the hostname (including the first slash) comprise
       the _path_.

       Note that the query string (the key-value pairs following `?`) can be
       included as part of the path for this lab.

A recommended approach for parsing HTTP request is to isolate different parts
of the request by finding the start and end patterns for each component using
`strstr()`.  Here are some examples to get you started.

```c
char method[16];
// The first thing to extract is the method, which is at the beginning of the
// request, so we point beginning_of_thing to the start of req.
char *beginning_of_thing = req;
// Remember that strstr() relies on its first argument being a string--that
// is, that it is null-terminated.
char *end_of_thing = strstr(beginning_of_thing, " ");
// At this point, end_of_thing is either NULL if no space is found or it points
// to the space.  Because your code will only have to deal with well-formed
// HTTP requests for this lab, you won't need to worry about end_of_thing being
// NULL.  But later uses of strstr() might require a conditional, such as when
// searching for a colon to determine whether or not a port was specified.
//
// Copy the first n (end_of_thing - beginning_of_thing) bytes of
// req/beginning_of_things to method.
strncpy(method, beginning_of_thing, end_of_thing - beginning_of_thing);
// Move beyond the first space, so beginning_of_thing now points to the start
// of the URL.
beginning_of_thing = end_of_thing + 1;
// Continue this pattern to get the URL, and then extract the components of the
// URL the same way.
...
```


### Testing

The `test_parser()` function was built for you to test the HTTP parsing code.
It provides four scenarios: complete HTTP request with default port; complete
HTTP request with explicit port and query string; complete request with dotless
hostname, and incomplete HTTP request.

Compile your proxy code by running the following:

```bash
make
```

Then run the following to see that it behaves as you would expect it to:

```bash
./proxy
```


### Checkpoint 1

Use output from your print statements to verify that your code has extracted
the components of the HTTP request properly.

Now would be a good time to save your work, if you haven't already.

At this point, remove or comment out the call to `test_parser()` in `main()`;
it was just used for testing.


## Part 2 - Sequential HTTP Proxy

As you implement this section, you might find it helpful to refer to the TCP
code from the
[sockets homework assignment](../07-hw-sockets) and the
[HTTP homework assignment](../09a-hw-http).


### Receiving the HTTP Request

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

   - `bind()` it to a port passed as the first argument from the
     command line, and configure it for accepting new clients with `listen()`.

   - Return the file descriptor associated with the server socket.
 - `handle_client()` - Given a newly created file descriptor, returned from
   `accept()`, handle a client HTTP request.  For now, just have this method do
   the following:
   - Read from the socket into a buffer until the entire HTTP request has been
     received.  Again, there is no request body in this lab, so this is
     basically just the end of headers.  The size of the request will not
     exceed 1024 bytes.
   - Print out the HTTP request using `print_bytes()`.  This will allow you to
     see the entire request.
   - Add a null-terminator to the HTTP request, and pass it to the
     `parse_request()` function, allowing it to extract the individual values
     associated with the request.
   - Print out the components of the HTTP request, once you have received it in
     its entirety (e.g., like `test_parser()` does).  This includes the method,
     hostname, port, and path.  Because these should all be null-terminated
     strings of type `char []`, you can use `printf()`.
   - Close the socket.
   Later will you replace printing the values with more meaningful
   functionality. This first part is just to get you going in the right
   direction.

Now flesh out `main()` such that it calls `open_sfd()` then uses a `while(1)`
loop to do the following:
 - `accept()` a client connection
 - call `handle_client()` to handle the connection

At this point, there are no threads, no concurrency, and no HTTP response.
But you should be able to get a sense for how your HTTP proxy is progressing.

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
```bash
curl -x http://localhost:port/ "http://localhost:5599/cgi-bin/slowsend.cgi?obj=lyrics"
```
```bash
./slow-client.py -x http://localhost:port/ -b 1 "http://www-notls.imaal.byu.edu/cgi-bin/slowsend.cgi?obj=lyrics"
```
```bash
./slow-client.py -x http://localhost:port/ -b 1 "http://localhost:5599/cgi-bin/slowsend.cgi?obj=lyrics"
```


### Checkpoint 2

Use output from your print statements to verify that 1) your HTTP proxy has
received the entire HTTP request and 2) your HTTP proxy has extracted the
components of the HTTP request properly.  This is particularly important in
this section because `slow-client.py` _guarantees_ that you will not have
received the entire HTTP request with your first call to `recv()`.  Make sure
that every byte of the printed values makes sense.  If not, now is the time to
fix it.

Now would be a good time to save your work, if you haven't already.


### Creating an HTTP Request

Now that your HTTP proxy has received the entire HTTP request, you can modify
your `handle_client()` code to create the HTTP request to send to the server.
This request will be slightly different from the one your HTTP proxy received
from the client.  The HTTP request your proxy received from the client looked
something like this:

```
GET http://www-notls.imaal.byu.edu:5599/cgi-bin/slowsend.cgi?obj=lyrics HTTP/1.1
Host: www-notls.imaal.byu.edu:5599
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:97.0) Gecko/20100101 Firefox/97.0

```

(Some things will differ, like the "User-Agent" header, which identfies your
client, and the port used.)

The _HTTP proxy_ requires the client to send a _full URL_.  However, an
_HTTP server_ requires the client to only send the _path_ (including query
string).  Additionally, the HTTP proxy will only use protocol HTTP/1.0, and
the "Connection" and "Proxy-Connection" headers should be added.  These further
enforce HTTP/1.0 behavior, which is discussed in the
[next section](#communicating-with-the-http-server).

Here is an example of the modified request:

```
GET /cgi-bin/slowsend.cgi?obj=lyrics HTTP/1.0
Host: www-notls.imaal.byu.edu:5599
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:97.0) Gecko/20100101 Firefox/97.0
Connection: close
Proxy-Connection: close

```

To simplify your request parsing and creation, you may simply replace _all_
headers that were sent by the client and create your own "Host", "User-Agent",
"Connection", and "Proxy-Connection" headers, as shown above.  A sample value
for "User-Agent" is provided in your `proxy.c` file.  The value for the "Host"
field will be either `hostname:port` or simply `hostname`, if the port is the
default HTTP port.  For example:

```
Host: www-notls.imaal.byu.edu:5599
```

or

```
Host: www-notls.imaal.byu.edu
```
In the second example, port 80 is implied.

In summary, for the new HTTP request that was created:
- The URL in the first line, as received from the client, was changed to be a
  path (plus query string).
- The protocol is always "HTTP/1.0" (this simplifies the client-server
  interaction for the purposes of this lab).
- The headers from the client may be completely replaced with "Host",
  "User-Agent", "Connection", and "Proxy-Connection" headers that are generated
  by the proxy, for simplicity.

Remember that all lines in an HTTP request end with a carriage-return-newline
sequence, `\r\n`, and the HTTP request headers are ended with
the end-of-headers sequence, `\r\n\r\n` (i.e., a blank line after the last
header).

Use `print_bytes()` to print out the HTTP request you created.  Then re-build
and re-start your proxy, and make sure it works properly when you run the
following:

(NOTE: the commands below are still expected to fail.  This is just to test
your HTTP request.)

(Replace "port" with the port on which your HTTP proxy is listening.)

```bash
curl -x http://localhost:port/ "http://www-notls.imaal.byu.edu:5599/cgi-bin/slowsend.cgi?obj=lyrics"
```
```bash
curl -x http://localhost:port/ "http://www-notls.imaal.byu.edu/cgi-bin/slowsend.cgi?obj=lyrics"
```
```bash
./slow-client.py -x http://localhost:port/ -b 1 "http://www-notls.imaal.byu.edu/cgi-bin/slowsend.cgi?obj=lyrics"
```
```bash
./slow-client.py -x http://localhost:port/ -b 1 "http://localhost:5599/cgi-bin/slowsend.cgi?obj=lyrics"
```


### Checkpoint 3

Use output from your print statements to verify that your HTTP proxy has
successfully created the HTTP request that it will send to the server, based on
the HTTP request that it received from the client.  Check for every character,
including the final `\r\n\r\n`.  If things don't check out, now is the time to
fix things.

Now would be a good time to save your work, if you haven't already.


### Communicating with the HTTP Server

With the modified HTTP request prepared, you can now communicate with the HTTP
server.  Modify your `handle_client()` function again:

 - Use `getaddrinfo()` and `connect()` to create a *new* TCP (`SOCK_STREAM`)
   socket and establish a connection with the HTTP server (i.e., the host and
   port specified by the client in its request).  This does not replace the
   socket with the client; the HTTP proxy is now communicating with both
   client *and* server concurrently, using a dedicated socket for each
   connection.
 - Send the newly created HTTP request over the socket connected to the server.
 - Receive the HTTP response from the server.  Just like when the HTTP proxy
   received the request from the client, the proxy will need to loop and
   continue reading from the server socket until the entire response has been
   received. The size of the response will not exceed 16384 bytes.

   With HTTP/1.0 (what is being used in *this* lab), only *one* request is made
   over a given TCP connection.  Thus, when the server has sent all it has to
   send (the entire HTTP response), it closes the connection--as opposed to
   waiting for another HTTP request.  An HTTP/1.0 client (in this case, the
   HTTP proxy) therefore knows when it has received the entire HTTP response
   when `read()` or `recv()` returns 0 (i.e., the indicator that the other side
   has called `close()` on the socket).

   A client-server pair using a more modern HTTP version (i.e., HTTP/1.1 or
   higher) might exchange several request-response transactions over the same
   TCP connection, which case, the "Content-Length" header (and/or other modern
   conventions) would need to be consulted to determine when the server was
   finished sending a given response.  But again, for _this_ lab, that is not
   necessary.  It is sufficient to stop reading when `read()` or `recv()`
   returns 0.
 - Print out the HTTP response using `print_bytes()`.  This will allow you to
   see the entire response.
 - Close the socket associated with the HTTP server.

Now re-build and re-start your proxy, and make sure it works properly when you
run the following:

(NOTE: the commands below are still expected to fail.)

(Replace "port" with the port on which your HTTP proxy is listening.  Note also
that the URLs containing "localhost:5599" have been removed.  Those were for
testing the parsing of HTTP requests, but there is currently no HTTP server
lisening on localhost:5599.)

```bash
curl -x http://localhost:port/ "http://www-notls.imaal.byu.edu/cgi-bin/slowsend.cgi?obj=lyrics"
```
```bash
./slow-client.py -x http://localhost:port/ -b 1 "http://www-notls.imaal.byu.edu/cgi-bin/slowsend.cgi?obj=lyrics"
```


### Checkpoint 4

Use output from your print statements to verify that your HTTP proxy has
received the entire HTTP response from the HTTP server.  This is particularly
important in this section because `/cgi-bin/slowsend.cgi` _guarantees_ that you
will not have received the entire HTTP response with your first call to
`recv()`.  Make sure that every byte of the printed values makes sense.  If
not, now is the time to fix it.

Now would be a good time to save your work, if you haven't already.


### Returning the HTTP Response

To complete `handle_client()`, send the HTTP response back to the client,
exactly as it was received from the server--no further manipulation needed.
Once you have done it, call `close()` on the socket associated with the client.
Your proxy is using HTTP/1.0, so there will be no further HTTP requests over
the existing connection.


### Checkpoint 5

At this point you should be able to pass:
 - [Tests performed against a non-local HTTP server](#manual-testing---non-local-server).
 - [Tests performed against a local HTTP server](#manual-testing---local-server).
 - [Automated tests](#automated-testing) with the following command:
   ```bash
   ./driver.py -b 60 threadpool
   ```


## Part 3 - Threaded HTTP Proxy

Once you have a working sequential HTTP proxy, alter it to handle multiple
requests concurrently by spawning a new thread per client.  Formulate your main
loop so that every time a new client connects (i.e., `accept()` returns)
`pthread_create()` is called.  You will want to define a thread function that
is *passed to* `pthread_create()` (i.e., its third argument) and calls
`handle_client()`,  after which it waits for a new client.

Note that with this particular thread paradigm, you should run your threads in
detached mode to avoid memory leaks.  When a new thread is spawned, you
can put it in detached mode by calling within the thread routine itself:
```c
pthread_detach(pthread_self());
```

Refer to the
[concurrency homework assignment](../09b-hw-concurrency)
for examples and code that you can integrate.


### Checkpoint 6

At this point you should be able to pass:
 - [Tests performed against a non-local HTTP server](#manual-testing---non-local-server).
 - [Tests performed against a local HTTP server](#manual-testing---local-server).
 - [Automated tests](#automated-testing) with the following command:
   ```bash
   ./driver.py -b 60 -c 35 multithread
   ```


## Part 4 - Threadpool

Now that you have some experience with multi-threaded server, change your proxy
server to use a pool of threads to handle concurrent HTTP requests instead of
launching a new thread for each request.

When the program starts, initialize eight consumer threads, a shared buffer
(queue) with five slots, and the associated semaphores and other shared data
structures to prepare the producer and consumers for handling concurrent
requests.  Formulate your producer loop, so that every time a new client
connects (i.e., `accept()` returns), the socket file descriptor returned is
handed off to one of the consumers, after which it waits for a new client by
calling `accept()` again.  You will need to modify your thread function so that
instead of handling a single client, it continually loops, waiting on new
clients from the shared buffer (queue) and handling them in turn.

Again, refer to the
[concurrency homework assignment](../09b-hw-concurrency)
for examples and code that you can integrate.


### Checkpoint 7

At this point you should be able to pass:
 - [Tests performed against a non-local HTTP server](#manual-testing---non-local-server).
 - [Tests performed against a local HTTP server](#manual-testing---local-server).
 - [Automated tests](#automated-testing) with the following command:
   ```bash
   ./driver.py -b 60 -c 35 threadpool
   ```


# Testing

Some tools are provided for testing--both manual and automated:

 - A python-based HTTP server
 - A driver for automated testing


## Manual Testing - Non-Local Server

Testing your HTTP proxy against a production HTTP server will help check its
functionality.  To test basic, sequential HTTP proxy functionality, first run
the following to start your HTTP proxy:

```bash
./proxy port
```

`curl` is a command-line HTTP client, described more in the
[HTTP homework assignment](../09a-hw-http).
For the purposes of this section, `curl` creates and sends an HTTP request to
your HTTP proxy, which is designated with `-x`.  

The `./slow-client.py` script  acts like `curl`, but it spreads its HTTP
request over several calls to `send()` to test the robustness of your proxy
server in reading from a byte stream.  The `-b` option designates the amount of
time (in seconds) that it will sleep in between lines that it sends.

The `-o` option tells `curl` and `slow-client.py` to save the contents of the
requested URL to the specified file (e.g., `tmp1`, `tmp2`, etc.), rather than
printing the contents to standard output.

In another window on the same machine, run the following:

```bash
curl -o tmp1 http://www-notls.imaal.byu.edu/index.html
```
```bash
./slow-client.py -o tmp2 -b 1 http://www-notls.imaal.byu.edu/index.html
```
```bash
curl -o tmp3 "http://www-notls.imaal.byu.edu/cgi-bin/slowsend.cgi?obj=lyrics"
```
```bash
./slow-client.py -o tmp4 -b 1 "http://www-notls.imaal.byu.edu/cgi-bin/slowsend.cgi?obj=lyrics"
```
```bash
curl -o tmp5 http://www-notls.imaal.byu.edu/images/imaal-80x80.png
```

At this point, the files `tmp1` through `tmp5` contain the contents returned by
`curl` retrieving the contents directly from the HTTP servers specified, i.e.,
without going through an HTTP proxy.

Now run the following:

(Replace "port" with the port on which your HTTP proxy is running.)

```bash
curl -o tmp1p -x http://localhost:port/ http://www-notls.imaal.byu.edu/index.html
```
```bash
./slow-client.py -o tmp2p -x http://localhost:port/ -b 1 http://www-notls.imaal.byu.edu/index.html
```
```bash
curl -o tmp3p -x http://localhost:port/ "http://www-notls.imaal.byu.edu/cgi-bin/slowsend.cgi?obj=lyrics"
```
```bash
./slow-client.py -o tmp4p -x http://localhost:port/ -b 1 "http://www-notls.imaal.byu.edu/cgi-bin/slowsend.cgi?obj=lyrics"
```
```bash
curl -o tmp5p -x http://localhost:port/ http://www-notls.imaal.byu.edu/images/imaal-80x80.png
```

Because we used `-x` to designate an HTTP proxy, the files `tmp1p` through
`tmp5p` now contain the contents returned by `curl` retrieving the contents
from the HTTP servers through an HTTP proxy--your HTTP proxy!

Using the `diff` command, we can see if there are any differences between the
files received by communicating with the HTTP servers directly and those
received from the HTTP servers through the HTTP proxy.  There should not be any
differences.

```bash
diff -u tmp1 tmp1p
```
```bash
diff -u tmp2 tmp2p
```
```bash
diff -u tmp3 tmp3p
```
```bash
diff -u tmp4 tmp4p
```
```bash
diff -u tmp5 tmp5p
```

Don't forget to remove them:

```bash
rm tmp1 tmp1p tmp2 tmp2p tmp3 tmp3p tmp4 tmp4p tmp5 tmp5p
```


## Manual Testing - Local Server

While testing on "non-local" HTTP servers is useful, using a local HTTP server
is helpful for testing right on your local machine.  To use a python-based HTTP
server for testing:

 1. Compile the CGI program in the `www/cgi-bin` sub-directory:

    ```
    make -C www/cgi-bin/
    ```

    Note: using the `-C` option with `make` changes the directory on which to
    operate from the current directory to the one specified.

 2. Start the HTTP server:

    (Replace "port2" with the port returned by `./port-for-user.pl` -- plus
    one.  For example, if `./port-for-user.pl` returned 1234, then use 1235.
    This allows you to use a *pair* of ports that are unlikely to conflict with
    those of another user--one for your HTTP server and one for the HTTP
    server.)

    ```
    python3 -m http.server -d www --cgi port2
    ```

    See the [HTTP Homework](../09a-hw-http#preparation) for more information on
    using this server.

 3. While the HTTP server is running in one window or pane, start your proxy
    server in another:

    (Replace "port" with the port returned by `./port-for-user.pl`.)

    ```bash
    ./proxy port
    ```

With the HTTP server running on one port (`port2`) and your HTTP proxy
running on another port (`port`), both on the same system, try running the
following:

(Replace "port2" with the port on which the HTTP server is running.)

```bash
curl -o tmp1 http://localhost:port2/foo.html
```
```bash
curl -o tmp2 http://localhost:port2/bar.txt
```
```bash
curl -o tmp3 http://localhost:port2/socket.jpg
```
```bash
curl -o tmp4 "http://localhost:port2/cgi-bin/slow?sleep=1&size=4096"
```
```bash
./slow-client.py -o tmp5 "http://localhost:port2/cgi-bin/slow?sleep=1&size=4096"
```

Now run the following:

(Replace "port" with the port on which your HTTP proxy is running and "port2"
with the port on which the HTTP server is running.)

```bash
curl -o tmp1p -x http://localhost:port/ http://localhost:port2/foo.html
```
```bash
curl -o tmp2p -x http://localhost:port/ http://localhost:port2/bar.txt
```
```bash
curl -o tmp3p -x http://localhost:port/ http://localhost:port2/socket.jpg
```
```bash
curl -o tmp4p -x http://localhost:port/ "http://localhost:port2/cgi-bin/slow?sleep=1&size=4096"
```
```bash
./slow-client.py -o tmp5p -x http://localhost:port/ "http://localhost:port2/cgi-bin/slow?sleep=1&size=4096"
```

Now use the `diff` command to see if there are any differences between the
files received by communicating with the HTTP servers directly and those
received from the HTTP servers through the HTTP proxy.  There should not be any
differences.

```bash
diff -u tmp1 tmp1p
```
```bash
diff -u tmp2 tmp2p
```
```bash
diff -u tmp3 tmp3p
```
```bash
diff -u tmp4 tmp4p
```
```bash
diff -u tmp5 tmp5p
```

Don't forget to remove them:

```bash
rm tmp1 tmp1p tmp2 tmp2p tmp3 tmp3p tmp4 tmp4p tmp5 tmp5p
```


## Automated Testing

For your convenience, a script is provided for automated testing.  You can use
it by running the following:

```bash
./driver.py -b 60 -c 35 threadpool
```

The `-b` option specifies the points awarded for basic HTTP functionality, and
the `-c` option specifies the points awarded for handling concurrent client
requests.

Basic HTTP functionality involves requesting text and binary content over HTTP
via the HTTP proxy, both from the local HTTP server and non-local HTTP
servers, using both `curl` and `slow-client.py`  It downloads several resources
directly and via the proxy and checks them just as shown previously.

The concurrency test has two parts:
 - Issue a single request of the HTTP proxy while it is busy with another
   request.
 - Issue five slow requests followed by five quick requests, to show that the
   fast requests are returned before the five slow requests.

Note that the driver can run with different options to help you troubleshoot.
For example:
 - *Basic Only*.  If you are just testing the basic functionality of your proxy
   (i.e., without concurrency), just use the `-b` option.
   ```bash
   ./driver.py -b 60 threadpool
   ```
 - *Increased Verbosity.*  If you want more output, including descriptions of
   each test that is being performed, use `-v`:
   ```bash
   ./driver.py -v -b 60 -c 35 threadpool
   ```
   For even more output, including the commands that are being executed, use
   `-vv`:
   ```bash
   ./driver.py -vv -b 30 -c 35 threadpool
   ```
 - *Proxy Output.*  If you want the output of your proxy to go to standard
   output, use the `-p -` option.
   ```bash
   ./driver.py -p - -b 60 -c 35 threadpool
   ```
 - *Downloaded Files.*  By default, the downloaded files are saved to a
   temporary directory, which is deleted after the tests finish--so your home
   directory does not get bloated.  If you want to keep these files to inspect
   them, use the `-k` option.
   ```bash
   ./driver.py -k -b 60 -c 35 threadpool
   ```
   If you use this option, be sure to delete the directories afterwards!

Any of the above options can be used together.


# Debugging Hints

 - Check the return values to all system calls, and use `perror()` to print out
   the error message if the call failed.  Sometimes it is appropriate to call
   `exit()` with a non-zero value; other times it is more appropriate to clean
   up and move on.
 - Place helpful print statements in your code, for debugging.  Use
   `fprintf(stderr, ...)` to print to standard error.
 - Use the `-p -` option  with `driver.py`, which will send all of your proxy
   output to standard output, so you can see your debug statements on the
   terminal just as you can see them outside the terminal.
 - When printing out what you are sending or receiving, print it out
   _immediately_ before calling `send()` or `recv()`.
 - If you are getting unexpected values for the lengths of data received --
   particularly for the image files -- ensure that you are not using
   `strlen()`, except on _null-terminated strings_.  For data read from a
   socket, you should be using the return value of `recv()` to determine how
   much you have read.  Only use `strlen()` if 1) you are sure that the bytes
   you are wanting to measure have no null byte values (and typically, you are
   wanting to read ASCII characters) and 2) the sequence of bytes you are
   wanting to measure are immediately followed by a null byte.  This null byte
   will not be included in data read from a socket; it will be only be there if
   placed by your code.
 - Often it can be helpful to initialize you buffers before use.  You can use
   `bzero()` for this.  See the man page for `bzero(3)` for more.
 - If you get the following error:

   ```
   __main__.MissingFile: File "./www/cgi-bin/slow" not found
   ```

   run the `make` command specified in the
   [Manual Testing](#manual-testing---non-local-server) section.
 - If the `slow-client.py` is printing the following error:

   ```
   ConnectionResetError: [Errno 104] Connection reset by peer
   ```

   it is because the other end of the connection (the client-to-proxy socket on
   your proxy) has been closed before all the data was read.  That means that
   your proxy is not reading the full request sent by the client.  Remember
   that `slow-client.py` sends the request slowly, over multiple calls to
   `send()`.  For this reason, your proxy _must_ call `recv()` multiple times
   to receive the full request and empty the buffer.  The only way for your
   proxy to know that it has received the entire request is by looking for the
   end-of-headers sequence (`"\r\n\r\n"`).
 - If the python-based HTTP server results in the following error:

   ```
   ConnectionResetError: [Errno 104] Connection reset by peer
   ```

   it is because the other end of the connection (the proxy-to-server socket on
   your proxy) has been closed before all the data was read.  That means that
   your proxy is not reading the full response from the server.  Remember that
   for some of the URLs requested, the responses are sent slowly, over multiple
   calls to `send()`.  For this reason, your proxy _must_ call `recv()`
   multiple times to receive the full response and empty the buffer.  The only
   way for your proxy to know that it has received the entire response is when
   `recv()` returns 0, indicating that the server has closed its end of the
   connection.
 - If the driver reports that files differ, use the `-k` option to "keep" the
   files retrieved from the server and through the proxy server; they are
   otherwise deleted automatically to keep them from cluttering up your
   filesystem.  They will be stored with some funny-looking names to keep them
   from accidentally overwriting other files on your system.  Then use `ls -l`
   to look at file sizes.  Often that is enough to point you in the right
   direction.  If you need more, use `cat` to show you the file contents and/or
   `diff -u` to look at the actual content differences.
 - If the driver reports that the slow files were retrieved before the fast
   files, add some print statements to your code to show the progress for each
   state of the request handling: receiving the request, sending the request,
   receiving the response, sending the response.  You should see the states for
   the slow requests (which start first) interrupted by the states for the fast
   request (which start later), such that the slow requests finish last.

   A few things to look for when troubleshooting this problem:

   - Make sure that your proxy is reading the entire HTTP request from the
     client.  If that's the case, then the slow requests might actually finish
     faster.
   - If it works when you spawn threads on-the-fly but not with the threadpool,
     then make sure your threadpool has enough threads and slots.
     See [Part 4 - Threadpool](#part-4---threadpool).
 - If `curl` prints the following error:

   ```
   Received HTTP/0.9 when not allowed
   ```

   it is likely because your proxy is sending an invalid HTTP response back to
   the client.  Call `print_bytes()` to print the the contents of your response
   immediately before calling `send()` to send your response, to see what is
   being sent.


# Evaluation

Your score will be computed out of a maximum of 100 points based on the
following distribution:

 - 60 for basic HTTP proxy functionality
 - 35 for handling concurrent HTTP proxy requests using a threadpool
 - 5 - compiles without any warnings

Run the following to check your implementation on one of the CS lab machines:

```b
./driver.py -b 60 -c 35 threadpool
```


# Submission

Upload `proxy.c` to the assignment page on LearningSuite.
