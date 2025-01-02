# HTTP

The purpose of this assignment is to give you hands-on experience with
HTTP.  As part of the assignment, you will identify the different parts of a
URL and will use the command-line program `curl` to experiment with HTTP on a
local HTTP server.


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

    - Section 11.5 in the book

    Additionally, man pages for the following are also referenced throughout the
    assignment:

    - `curl(1)`
    - `getaddrinfo(3)`
    - `ascii(7)`

 2. Either log on to a BYU CS lab workstation directly or log on remotely using
    SSH.  To log in using `ssh`, open a terminal and use the following `ssh`
    command:

    (Replace "username" with your actual CS username)

    ```bash
    ssh username@schizo.cs.byu.edu
    ```

    The exercises in this assignment will only work if run from a CS lab
    machine.

 3. Start a tmux session.  Create two panes, such that the window looks like
    this:

    ```
    -------------------------------------
    |                                   |
    |           HTTP Client             |
    |                                   |
    -------------------------------------
    |                                   |
    |           HTTP Server             |
    |                                   |
    -------------------------------------
    ```

 4. On the bottom "HTTP Server" pane, use SSH to remotely log on to a CS lab
    machine _different_ from the one you are already on.  See a list of machine
    names [here](https://docs.cs.byu.edu/doku.php?id=open-lab-layout):

    Fall 2023 Note: At the moment, only machines within the "States" and
    "Marvel" labs appear to be reliable choices.

    (Replace "username" with your actual CS username and "hostname" with the
    name of the host to which you wish to log on.)

    ```bash
    ssh username@hostname
    ```

 5. In the "HTTP Server" (lower) pane, use `cd` to navigate to the directory
    associated with this assignment.

 6. In the "HTTP Server" (lower) pane, run the following:

    (Replace "port" with a port of your choosing, an integer between 1024 and
    65535.  Use of ports with values less than 1024 require root privileges.)

    ```
    python3 -m http.server -d www --cgi port
    ```

    This starts a python-based HTTP server in the directory "www" (specified
    with the `-d` option) listening on the TCP port that you designated.  The
    `--cgi` option tells the server to support CGI.  That means that paths
    starting with "/cgi-bin/" should be treated as CGI programs; that is, they
    are executed by the server and their output sent back to the client--as
    opposed the server sending their file contents to the client.  Note that
    this HTTP server uses HTTP/1.0.  For the purposes of this assignment, the
    difference between HTTP/1.1 and HTTP/1.0 is that an HTTP/1.1 server can
    receive multiple requests, back-to-back, over the same TCP connection,
    whereas an HTTP/1.0 server closes its end of the connection after
    transmitting the entire HTTP response.  In this latter case, the client's
    call to `read()` results in a return value of 0, which is, effectively,
    end-of-file (EOF).


# Part 1: HTTP

In this section you will use `curl` to experiment with the HTTP protocol.
`curl` is a command-line HTTP client.  It parses the provided URL, prepares a
client socket, connects to the designated server, sends an HTTP request over
the socket, receives the HTTP response from the server, and prints the response
body to standard output.  Various options will be used with `curl` in the
instructions that follow.

For each of the URLs that follow, run the following command, but replace "host"
and "port" with the hostname and port on which you are running your server, and
"url" with the designated URL.  Also replace "output\_a.txt" with a filename
unique to the URL you are retrieving.  

```
curl -s -v url > output_a.txt 2>&1
```

The `-s` option tells `curl` to suppress the progress bar.  The `-v` tells
`curl` to print the HTTP request headers and the HTTP response headers to
standard error--in addition to printing the HTTP response body to standard
output, which is the default. Finally, adding `2>&1` duplicates the standard
error onto standard output.  Thus, when output redirection has been applied,
the output of both streams will go to the file.

URLs:

 a. `http://host:port/foo.html`

 b. `http://host:port/bar.txt`

 c. `http://host:port/socket.jpg`

 d. `http://host:port/does-not-exist`

For the following URL, run the `curl` command again, with a few additions, in
particular the use of the `-d` option and the double quotes around the URL and
the argument to `-d`.  Without the quote, the shell would interpret the `&` as
a background operator!

```
curl -s -v -d "username=user&password=pw" "url" > output_e.txt 2>&1
```

When the `-d` option is used, the request type used by `curl` is changed from
"GET" to "POST", and `curl` sends the bytes that follow as a request body. 

URLs:

 e. `http://host:port/cgi-bin/myprog?univ=byu&class=CS324&msg=hello%3Dworld%21`

Use the output from running the `curl` commands on the URLs to answer the
questions that follow.  The output you see for each use of the `curl` command
can be explained as follows:

 - Lines beginning with ">" are bytes sent by the client to the server as part
   of the request headers.
 - Lines beginning with "}" summarize the bytes sent by the client to the
   server as part of the request body (if any).
 - Lines beginning with "<" are bytes sent by the server to the client as part
   of the response headers.
 - Lines beginning with "{" summarize the bytes sent by the server to the
   client as part of the response body.
 - Lines beginning with "\*" are debug information.

Note that you can use `cat` with the `-v` option to show carriage return
characters (i.e., `'\r'`) as `^M`.  Newline characters (i.e., `'\n'`), however,
are implied by the presence of a new line.  For example, consider the following
command and its output:

```
$ cat -v myfile.txt
This is a line^M
Followed by another line
```

In this case, `cat` shows the presence of both a carriage return (`'\r'`) and a
newline (`'\n'`) between the first and second line--the former with a `^M` and
the latter by the fact that the second line is shown below the first.

You can use `cat -v` to help you analyze the output when answering the
questions.  For example: `cat -v output_a.txt`.

Questions:

 1. How does the server know when it has received all the headers associated
    with the HTTP request?

 2. How does the server know when it has received the entire HTTP request body,
    if any?

 3. What numerical response code indicates that the server was able to find the
    requested path?

 4. What numerical response code indicates that the server was unable to find
    the requested path?

 5. How does the client know when it has received all the headers associated
    with the HTTP response?

 6. How does the client know when it has received the entire response body?

 7. How does the client know the type of the content returned by the server, so
    that it (the client) can render it properly?

 8. For URL (a), what type of content is returned in the response body?

 9. For URL (b), what type of content is returned in the response body?

 10. For URL (e), what type of content is returned in the response body?

 11. For URL (a), how large (i.e., how many bytes) is the response body?

 12. For URL (b), how large (i.e., how many bytes) is the response body?

 13. For URL (e), how large (i.e., how many bytes) is the response body?


# Part 2: URLs

Consider the following URLs to answer the questions that follow.  Unlike the
previous section, you will not be retrieving them using `curl` or any other
HTTP client.  Rather, these URLs are simply used as examples for reviewing the
concepts of URLs in relation to HTTP requests.

URLs:

 f. `http://example.com/foo.html`

 g. `http://example.com:1234/bar.txt`

 h. `http://localhost/socket.jpg`

 i. `http://example.com/cgi-bin/foo?univ=byu&class=CS324&msg=hello%3Dworld%21`

Note that to answer some questions it might be helpful to refer to the output
of the `curl` commands in the [previous section](#part-1-http).  Also note that
for all questions except 24 through 25, the answer comes directly from the URL
the in the question.

Questions:

 14. For URL (f), what hostname will an HTTP client pass to `getaddrinfo()`?

 15. For URL (h), what hostname will an HTTP client pass to `getaddrinfo()`?

 16. For URL (f), what remote port will an HTTP client pass to `connect()`?

 17. For URL (g), what remote port will an HTTP client pass to `connect()`?

 18. For URL (f), what is the complete path value that will be sent by the
     client in the first line of the HTTP request?

 19. For URL (i), what is the complete path value that will be sent by the
     client in the first line of the HTTP request?

 20. For URL (f), what value will be sent by the client as the value of the
     "Host" header?

 21. For URL (g), what value will be sent by the client as the value of the
     "Host" header?

 22. For URL (h), what value will be sent by the client as the value of the
     "Host" header?

 23. For URL (i), what is the value of the query string?  Note that the
     question mark (`?`) is not part of the query string.

For questions 24 and 25, refer to
[RFC 3986 Section 2.1](https://datatracker.ietf.org/doc/html/rfc3986#section-2.1),
which is the official specification for Uniform Resource Identifiers (URIs),
which is a more general category that includes URLs.  See also the man page for
`ascii(7)`.

 24. For URL (i), to what ASCII character will the character sequence "%3D" be
     decoded by a CGI program?

 25. For URL (i), to what ASCII character will the character sequence "%21" be
     decoded by a CGI program?


# Part 3: CGI

After the HTTP server parses the client request, if it determines from the path
sent that CGI should be used to run a program and generate dynamic content, the
HTTP server does the following:

 - Sends the first line and initial headers associated with the HTTP response.
 - `fork()` to create a child process;
 - `dup2()` to duplicate the socket onto standard input for reading the request
   body from the client;
 - `dup2()` to duplicate the socket onto standard output for writing the
   remaining response headers and the response body;
 - `setenv()` to set the value of the `QUERY_STRING` environment variable to
   the value of the query string sent by the client;
 - `setenv()` to set the value of the `CONTENT_LENGTH` environment variable to
   the value of the Content-Length header sent by the client (i.e., the size of
   the request body); and
 - `execve()` to actually run the program in the child process.

It is the job of the CGI program to use the inputs it received from the HTTP
server to send the remainder of the HTTP response headers and the HTTP response
body back to the HTTP client.  Section 11.5.4 in the book has additional
information on this.

For this part of the assignment, you will write a CGI program--that is, the one
that is executed by the HTTP server.  Call your program `myprog1.c`.  It should
have _mostly_ the same behavior as that you observed in `cgi-bin/myprog`.  See
the output from running the `curl` command against URL (e) above.

 - Retrieve the `CONTENT_LENGTH` and `QUERY_STRING` environment variables,
   which will have been set by the HTTP server using the `Content-Length`
   header and query string sent by the client, respectively.  If the
   `CONTENT_LENGTH` environment variable is found, then convert it to an
   integer using `atoi()`.

 - Read exactly `CONTENT_LENGTH` bytes from standard input into a buffer
   (`char []`).  That is your request body.  While normally the bytes in the
   request body might be anything, in this particular case, the bytes are ASCII
   text.  That means, in part, that there are no null values in the content.
   That also means that there will be no null terminating byte.  (A null
   terminating byte is a convention for a C string, not for HTTP request body.)
   Add a null byte at the end of the bytes read, so it can be used with string
   functions, such as `strlen()`.

 - Create the response body, so it contains the following contents:

   ```
   Hello CS324
   Query string: [query string goes here...]
   Request body: [request body goes here...]
   ```

   You might find the `sprintf()` function helpful for this.  Also, note that
   unlike with HTTP headers, each line in the body should simply end with
   `'\n'`; there is no need to include `'\r'`.

 - Send "Content-Type" and "Content-Length" headers of the HTTP response to the
   client.  The type should be "text/plain", and length is the total length of
   the response body--which includes all bytes after the end-of-headers
   sequence.  Because your content (created in the previous step) is a
   null-terminated string, you can find this using `strlen()`.  Each header
   should end with `"\r\n"`, and after the final header, there should be a
   blank line; that is, this character sequence should follow the last header:
   `"\r\n\r\n"`.

   Note that your CGI program is not responible for sending the first line of
   the response (e.g., the protocol, response code, etc.).  That line, along
   with any other initial headers, will have been sent by the server before it
   called `fork()` and `execve()`.

   Remember, the socket has been duplicated onto standard output.

 - Send the response body you created earlier.

Test your program by compiling it and placing the resulting binary in
`www/cgi-bin`.  Then run the same `curl` command line that you used for URL
(e) above, substituting "myprog1" for "myprog".  The response headers
(beginning with the "Content-Type" header) and the response body returned for
`myprog1` should match those for `myprog`, _byte for byte_, except that "Hello
world" will be replaced with "Hello CS324" in the body.

Try a few different values for the query string and the request body to see
that it works properly in each case.  Note that for different response body
values, you will need to update the `CONTENT_LENGTH` environment variable to
match.

Note that using skills you learned in the
[BYU bandit assignment](../02-hw-byu-bandit) you can also test your CGI program
_without_ an HTTP server.  That is, using the shell, you can artificially set
the environment variables that the CGI program expects, provide data to the
standard input of the CGI by using a pipe that is connected to the standard
output of another program (e.g., `echo`), and observe the output of the CGI
program on the terminal.  Of course, in the case of a CGI program that was
executed by an HTTP server, the output would have gone to the socket connected
to the client because that socket would have been duplicated onto standard
output.  But because standard has not been modified, here you will see it on
the terminal.

Using these concepts, your job is to determine how to run your CGI program as a
command-line pipeline, passing it the following inputs, as if it had been
executed (i.e., with `execve()`) by an HTTP server that understood CGI:

 - Query string: `univ=byu&class=CS324&msg=hello%3Dworld%21`
 - Request body: `username=user&password=pw`

Because previous assignments only involved a very simple use of environment
variables, please note the following additional information on environment
variables:

 - Quotes should be used to enclose values that contain spaces or other
   characters that might otherwise be interpreted by the shell.  For example,
   if you wanted to set the value of the environment variable `FOO` to
   `bar&baz`, the following is _incorrect_:

   ```
   FOO=bar&baz
   ```

   In the above example, the shell interprets `&` as the background operator
   for the command `FOO=bar`!

   This is the correct way to set the environment variable:

   ```
   FOO="bar&baz"
   ```

 - Multiple environment variables can be set by spacing-delimiting them.  For
   example:

   ```
   FOO="bar&baz" ABC="123 XYZ" cmd
   ```

 - If setting environment variables for a command in a pipeline, place the
   environment variables immediately before that command.  For example:

   ```
   cmd1 | FOO="bar&baz" ABC="123 XYZ" cmd2
   ```

The terminal output of your CGI program should include the last of the headers,
the end-of-headers sequence, and the response body.  When it looks right, given
the above inputs, add `sha1sum` to the end of the pipeline, so you get the
SHA1SUM of the CGI program output.

 26. What is the SHA1SUM of the output of the CGI program when run with the
     above inputs (query string and request body)?  Hint: it should start with
     `c0140d`.

 28. What is the command pipeline you used to run the CGI program with the
     above inputs and produce the SHA1SUM in the previous question?
