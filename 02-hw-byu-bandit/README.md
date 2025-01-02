# BYU Bandit

The purpose of this assignment is to familiarize you with working in a shell
environment, including redirection, pipelining, backgrounding, and more.  Read
the entire assignment before beginning!


# Maintain Your Repository

 Before beginning:
 - [Mirror the class repository](../01a-hw-private-repo-mirror), if you haven't
   already.
 - [Merge upstream changes](../01a-hw-private-repo-mirror#update-your-mirrored-repository-from-the-upstream)
   into your private repository.

 As you complete the assignment:
 - [Commit changes to your private repository](../01a-hw-private-repo-mirror#commit-and-push-local-changes-to-your-private-repo).


# Preparation

NOTE: Throughout this exercise, you _must_ run the `ssh` command on a BYU CS
lab machine, or you will get unexpected results.

Either log on to a BYU CS lab workstation directly or log on remotely using
SSH.  To log in using `ssh`, open a terminal and use the following `ssh`
command:

(Replace "username" with your actual CS username)

```bash
ssh username@schizo.cs.byu.edu
```


# Instructions

Follow these steps:

 1. Use the SSH program to log in remotely to the computer imaal.byu.edu with
    username `bandit0` and password `bandit0`:

    ```bash
    ssh bandit0@imaal.byu.edu
    ```

 2. Follow the instructions in the file `readme` to get the password for Level
    1 (hint: use `cat` to get started).

 3. Close out your session to log out of imaal.byu.edu (`ctrl`+`d` or `exit`).

 4. Use SSH to again log in to imaal.byu.edu, this time with username `bandit1`
    and the password you obtained for Level 1.

 5. Repeat steps 2 through 4 through Level 10, such that you can log in to
    imaal.byu.edu successfully as the `bandit10` user.

For each level, except Level 8 (i.e., as a the `bandit7` user), you need to use
a combination of input/output redirection and/or pipelining, such that you can
get a single pipeline command (i.e., a "one-liner") to output just the password
for the next level, on a single line.  In some cases, the pipeline might just
contain a single command (example: learning the password for Level 1).  For
most cases, however, more than one command is required.  For example, consider
the following pipeline:

```bash
grep bar somefile.txt | awk '{ print $8 }' | base64 -d
```

Note that three commands were used in the example pipeline above: `grep`,
`awk`, and `base64`.  The standard output of `grep` was connected to the
standard input of the `awk` command (via a pipe), and the standard output of
`awk` was connected to the standard input of the `base64` command (via a pipe).
There was no further command in the pipeline, so `base64`'s standard output
simply goes to the console.

When learning the password for Level 8 (i.e., as the `bandit7` user), the
suspend/resume does not need to be done as part of the "one-liner".  Those
require keystrokes after the program has been executed.  Just use the single
command.


# Submission Format

As you go, create a file `bandit.txt` that has the following format:

```bash
Level 0:
PASSWORD1
PIPELINE1
Level 1:
PASSWORD2
PIPELINE2
...
```

`PASSWORD1` represents the password for Level 1, and `PIPELINE1` is the actual
pipeline of commands (i.e., "one-liner") you used to get that password while
logged in as `bandit0`, etc.  For example:

```bash
Level 0:
0G3wlqW6MYydw4jQJb99pW8+uISjbJhe
foo
Level 1:
xJJHpfRpbE7F2cAt8+V9HLEoZEzZqvi+
grep bar somefile.txt | awk '{ print $8 }' | base64 -d
...
```

Note that following the format above is important, as it will allow your
assignment to be graded automatically.

Again, the pipeline for Level 8 does not require any more than what was used to
_start_ the command; you do not need to include what you did to suspend and
resume.


# Automated Testing

For your convenience, a script is also provided for automated testing.  This is
not a replacement for manual testing but can be used as a sanity check.  You
can use it by simply running the following:

```bash
./SshTester.py bandit.txt
```


# Helps

## Useful Commands

Here are some commands that you might use to help you:

 - `awk`
 - `base64`
 - `cat`
 - `curl`
 - `cut`
 - `dig`
 - `grep`
 - `gzip`
 - `head`
 - `md5sum`
 - `sha1sum`
 - `sort`
 - `tar`
 - `uniq`


## Building a Pipeline Incrementally

You might feel overwhelmed with the "pipeline" aspect of this assignment.  To
help you out, build the pipeline gradually.  For example, in the above example,
run just the following to see what the output is:

```bash
grep bar somefile.txt
```

Then run:

```bash
grep bar somefile.txt | awk '{ print $8 }'
```

Finally, when that is working, run the whole thing:

```bash
grep bar somefile.txt | awk '{ print $8 }' | base64 -d
```


## Other Helps

 - Use the man pages to learn about a command, as they are the primary
   documentation!  You can also find helpful examples on the Web.
 - To suspend the pipeline currently running in the foreground, use `ctrl`+`z`.
   Use `fg` to resume.  For more information, See the sections on
   `REDIRECTION`, `Pipelines` (under `SHELL GRAMMAR`), and `JOB CONTROL` in the
   `bash(1)` man page.
 - Where a pipelined command begins with a command that can receive input from
   standard input, and the initial input is a file, one way of doing it is to
   use `<` to open the file and send it to the standard input of the first
   command.  For example:
   ```bash
   cat < file.txt
   cat < file.txt | grep f
   ```
 - You can redirect standard output or standard error to `/dev/null` (or any
   file) by adding `> /dev/null` or `2> /dev/null`, respectively, to the end of
   a command.  What this says is that before the command is run, `/dev/null` is
   opened for writing and then file descriptor 1 (standard output, implied) or
   file descriptor 2 (standard error), respectively, should point to whatever
   file descriptor resulting from the newly-opened `/dev/null` file points to.
   (Also, `/dev/null` isn't actually a file but is really just a file-like
   device to "write" things that won't be kept.)  For example:
   ```bash
   echo foo > /dev/null
   echo foo 2> /dev/null
   echo foo 2> /dev/null | grep f
   ```
 - You can the duplicate standard error of a command onto its standard output
   by using `2>&1`.  What this is saying is that file descriptor 2 (standard
   error) should point to whatever file descriptor 1 (standard output) points
   to.  Something like this is useful for sending both standard output _and_
   standard error to the next command in a pipeline, rather than only the
   standard output.  With a pipelined command, redirecting standard output of
   the command to the pipe always happens before any file descriptor
   duplication.  For example:
   ```bash
   echo foo 2>&1
   echo foo 2>&1 | grep f
   ```
 - You combine redirection and duplication to send output from both standard
   output and standard error to the same file.  For example:
   ```bash
   echo foo > /dev/null 2>&1
   ```
   Note that the order here is that the standard output of `echo` is redirected
   to `/dev/null`, and then the standard error of `echo` is duplicated onto
   standard output.  If the order were reversed, you would get different results.
   Think about why that might be.
 - The `awk` command is pretty extensive and indeed includes a whole language.
   However, one of the common uses is to print one or more fields from every a
   space-delimited line of input.  For example, a simple `awk` script to print
   out just the second field of text from every line, the following command
   would work:
   ```bash
   awk '{ print $2 }'
   ```
 - `dig` and `curl` and are commands used to issue a request to a Domain Name
   System (DNS) server and HyperText Transfer Protocol (HTTP) server,
   respectively.  You can try them out with different domain names, types, or
   URLs, to see how they work, but you shouldn't need to do anything fancy with
   them for this assignment.  You will find the `+short` option useful for
   `dig`.  For example, to query for the `A` record for `example.com` use:
   ```bash
   dig +short example.com A
   ```


# Submission

Upload `bandit.txt` to the assignment page on LearningSuite.
