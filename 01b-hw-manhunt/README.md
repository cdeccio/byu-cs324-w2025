# `man` Hunt

This set of exercises is intended to familiarize you with `man`, which is the
gateway to the official documentation of programs, system calls, library calls,
and operating system features _for your running system_.


## Setup

NOTE: Throughout this exercise, you _must_ run the `man` command on a BYU CS
lab machine, or you will get unexpected results.

Either log on to a BYU CS lab workstation directly or log on remotely using
SSH.  To log in using `ssh`, open a terminal and use the following `ssh`
command:

(Replace "username" with your actual CS username)

```bash
ssh username@schizo.cs.byu.edu
```

Once logged in, run the following:

```bash
man man
```

Running this command opens a "pager" (i.e., a file viewer) that displays the
contents of the manual page for the program `man`.  With the default pager
(`less`), the following keys are helpful for navigation:

 - `h`: launch the built-in help
 - `j` (or down arrow): go down one line (mneumonic: the crook of the j points
   downward)
 - `k` (or up arrow): go up one line
 - `ctrl`+`f` (or page down): go down one screen (i.e., page down)
 - `ctrl`+`b` (or page up): go up one screen (i.e., page up)
 - `/`, `pattern`, `Enter`: search for `pattern` "forward" in the document.
   For example, typing "/foo" then `Enter` would find the next instance of
   "foo" in the document.
 - `?`, `pattern`, `Enter`: search for `pattern` "backward" in the document.
   For example, typing "?foo" then `Enter` would find the previous instance of
   "foo" in the document.
 - `n`: go to the next (if `/` was most recently used) or previous (if `?` was
   most recently used) instance of the pattern previously searched for
 - `q`: quit

Now read through the man page for `man`, especially the sections on "SYNOPSIS",
"DESCRIPTION", and "EXAMPLES".  See especially the `-f` and `-k` options.  You
will use those to answer questions in the next section!

To familiarize yourself the man page, go through the following examples while
still in the man page for `man`:

 - Find the first instance of "ENVIRONMENT" by typing "/ENVIRONMENT" then
   `Enter`.
 - Type "n" to go to the next instance of "ENVIRONMENT".  This one should be on
   the leftmost side of the screen (i.e., no indentation).  Its placement means
   that it is the heading for the section called "ENVIRONMENT".
 - Scroll downwards through the "ENVIRONMENT" section using the `j` key (down).
 - Find the previous instance of "man -k" by typing "?man -k" then `Enter`.
   Read the description.
 - Scroll upwards through the section you are currently in to find the title of
   the section.  It should be called "EXAMPLES".
 - Type "q" to exit the pager.
 - At the command line, enter the following to find all the man pages that
   include "echo" as a keyword:
   ```bash
   man -k echo
   ```
   Note that the argument passed to `-k` is a regular expression, so you might
   find that it returns words that _include_ "echo".  To limit the results to
   those that have exactly the keyword "echo", use the following:
   ```bash
   man -k '^echo$'
   ```
   (`^` signifies "start" and `$` signifies "end")
 - At the command line, enter the following to find all the man page sections
   for `printf`.
   ```bash
   man -f printf
   ```
 - At the command line, enter the following to open the man page in section 1
   for `printf`.
   ```bash
   man 1 printf
   ```
   Press "q" to quit.
 - At the command line, enter the following to open the man page in section 3
   for `printf`.
   ```bash
   man 3 printf
   ```
   Press "q" to quit.

Please note that the purpose of this exercise is not to have you learn all the
concepts referred to by the questions.  Rather, it is to familiarize you with
the `man` command, man pages, and official system documentation.


## Questions

Using only the `man` command, answer the following questions.  To answer each
question, you will need to call `man` with certain arguments and options and
either inspect the output or read parts of (or search within) the man page that
is opened.  If you are confused as to where to start, look at the examples in
the previous section.

 1. What are the numbers associated with the manual sections for executable
    programs, system calls, and library calls, respectively?
 2. Which section number(s) contain a man page for `kill`?
 3. Which section number(s) contain a man page for `exit`?
 4. Which section number(s) contain a man page for `open`?
 5. What three `#include` lines should be included to use the `open()` system
    call?
 6. Which section number(s) contain a man page for `socket`?
 7. Which `socket` option "Returns a value indicating whether or not this
    socket has been marked to accept connections with `listen(2)`"?
 8. How many short manual page descriptions contain the keyword `getaddrinfo`?
 9. According to the "DESCRIPTION" section of the man page for `string`, the
    functions described in that man page are used to perform operations on
    strings that are ________________. (fill in the blank)
 10. What is the return value of `strcmp()` if the value of its first argument
     (i.e., `s1`) is _greater than_ the value of its second argument (i.e.,
     `s2`)?
