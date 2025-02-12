# Shell Lab - Signals and Job Control

The purpose of this assignment is to help you become more familiar with the
concepts of process creation, signals, and job control.  To do this, you will
implement a shell like `bash` (GNU Bourne-Again SHell), which used in
operating systems like Linux.  This shell will read commands from standard
input and run the programs specified in those commands.  It will also support
multiple jobs.


# Maintain Your Repository

 Before beginning:
 - [Mirror the class repository](../01a-hw-private-repo-mirror), if you haven't
   already.
 - [Merge upstream changes](../01a-hw-private-repo-mirror#update-your-mirrored-repository-from-the-upstream)
   into your private repository.

 As you complete the assignment:
 - [Commit changes to your private repository](../01a-hw-private-repo-mirror#commit-and-push-local-changes-to-your-private-repo).


# Table of Contents

- [Getting Started](#getting-started)
  - [Reading](#reading)
  - [Resources Provided](#resources-provided)
  - [Reference Tiny Shell](#reference-tiny-shell)
  - [Functionality Not Included](#functionality-not-included)
  - [Your Tiny Shell](#your-tiny-shell)
  - [`tsh.c` Overview](#tshc-overview)
- [Instructions](#instructions)
  - [`builtin_cmd()`](#builtin_cmd)
  - [`eval()`](#eval)
  - [Checkpoint 1](#checkpoint-1)
  - [`sigchld_handler()`](#sigchld_handler)
  - [`waitfg()`](#waitfg)
  - [Checkpoint 2](#checkpoint-2)
  - [`sigint_handler()` and `sigtstp_handler()`](#sigint_handler-and-sigtstp_handler)
  - [Checkpoint 3](#checkpoint-3)
  - [`do_bgfg()`](#do_bgfg)
  - [Final Checkpoint](#final-checkpoint)
- [Helper Functions](#helper-functions)
  - [`parseline()`](#parseline)
  - [Job Handling Functions](#job-handling-functions)
- [Debugging Helps](#debugging-helps)
- [Automated Testing](#automated-testing)
- [Evaluation](#evaluation)
- [Submission](#submission)


# Getting Started

This section is intended to familiarize you with the concepts associated with
the lab and the resources provided to help you complete it, including a
walk-through usage of the reference shell.  You will begin coding in the
[instructions](#instructions) section.

## Reading

Read the following in preparation for this assignment:

 - Sections 8.2 - 8.5

Additionally, man pages for the following are also referenced throughout the
assignment:

 - `fork(2)`
 - `signal(7)`, `signal(2)`
 - `sigaction(2)`
 - `sigprocmask(2)`
 - `waitpid(2)`
 - `exec(3)`
 - `execve(2)`
 - `setpgid(2)`
 - `kill(1)`, `kill(2)`


## Resources Provided

 - `tsh.c` - a file containing a functional skeleton of a simple shell (i.e.,
   "tiny shell").  This is where you will do your work!
 - `Makefile` - a file used by the `make` command for building, cleaning, and
   performing automated testing of your code.
 - `tshref` - a binary file containing a reference implementation of tiny
   shell to demonstrate correct behavior.
 - `sdriver.pl` - a Perl script that runs a trace file against your shell to
   test its functionality.
 - `checktsh.pl` - a Perl script that uses `sdriver.pl` to run one or more
   trace files against both your shell and the reference implementation to see
   if their behaviors differ.
 - `trace01.txt` - `trace16.txt` - trace files for testing various aspects of
   your shell.
 - C programs to be run from _within_ your shell for testing its functionality.
   - `myspin.c` - Runs a `sleep()` loop for as many seconds as are specified on
     the command line.  Used as a program that simply "runs" for a defined
     amount of time.
   - `mysplit.c` - Calls `fork()` and then runs a `sleep()` loop for as many
     seconds as are specified on the command line, after which both parent and
     child terminate.  Used to test group membership.
   - `myint.c` - Runs a `sleep()` loop for as many seconds as are
     specified on the command line.  After that, sends a signal of type
     `SIGINT` to itself, causing it to terminate.  Used to test detection of
     change in process state from a signal received outside the shell.
   - `mystop.c` - Runs a `sleep()` loop for as many seconds as are
     specified on the command line.  After that, sends a signal of type
     `SIGTSTP` to itself, causing it to change to suspend execution (i.e.,
     change to state "stopped").  Used to test detection of change in process
     state from a signal received outside the shell.


## Reference Tiny Shell

This section walks through the reference shell behavior, so you know what you
will be implementing.  Run the reference shell by running the following from
your terminal:

```bash
./tshref
```

You will now see a prompt:

```bash
tsh>
```


### Foreground Jobs

Every time you type a command at the prompt, the shell will execute the
command.  What happens next depends on the presence (or absence) of the `&`
(_background_) operator at the end of the command line.  If no `&` operator is
found, then the shell runs the command as a _foreground_ job.  That means that
the shell waits until the command completes or its state changes before
printing the prompt and waiting for the next command to be entered.  If the
the process associated with the command terminates, the shell prints the prompt
again--an indicator that it is ready to receive and execute the next command.
For example:

```bash
tsh> /bin/sleep 10
tsh> 
```

Even though the first command took 10 seconds to complete, the prompt was not
returned until the command had completed.  We will talk about state changes a
little later.


### Background Jobs

When the `&` operator is used, the shell prints out a notice that the job is
running in the background, and the prompt is immediately printed, so the shell
can potentially read and evaluate another command even while the first is still
going!

```bash
tsh> /bin/sleep 10 &
[1] (1074) /bin/sleep 10 &
tsh>
```

The following is an explanation of the output resulting from running the
command:
 - `[1]` - the "job ID" of the new job created; the shell keeps track of all
   commands that are either _stopped_ (i.e., not currently scheduled to run) or
   _backgrounded_ (running, but not being "waited on" by the shell).  They
   differ from process IDs in that they are the _shell's_ way of keep track of
   "jobs", not the kernel's way of keeping track of processes.  Thus, they are
   specific to the running instance of the shell (i.e., they are not
   system-wide).  Job IDs are handed out sequentially, beginning with 1.
 - `(1074)` - the process ID of the (child) process created in connection with
   running the command specified on the command line.
 - `/bin/sleep 10 &` - the command entered on the command line, including the
   `&` operator.

If you enter `jobs` at the prompt while `/bin/sleep 10` is still running in the
background, you will see a list of all the currently stopped and
_backgrounded_ jobs, noting that there is, at the moment, only one:

```bash
tsh> jobs
[1] (1074) Running /bin/sleep 10 &
tsh>
```

Note that `jobs` is not referencing a file containing executable code; rather
it is a "built-in" command.  That is, it will run code within the shell itself,
rather than launching an external program called "jobs".  You will note that
`tsh.c` defines a global array of `struct job_t` called `jobs`, which maintains
the current list of jobs for the shell:

```c
struct job_t {              /* The job struct */
    pid_t pid;              /* job PID */
    int jid;                /* job ID [1, 2, ...] */
    int state;              /* UNDEF, BG, FG, or ST */
    char cmdline[MAXLINE];  /* command line */
};
struct job_t jobs[MAXJOBS]; /* The job list */
```

Thus, when `jobs` is entered at the command line, the shell runs the function
`listjobs()` (a helper function, already given to you), to iterate over the
array of jobs (i.e., `jobs`) and print out the information associated with
each.

If you wait longer than 10 seconds and then enter `jobs` again, the list will
have changed:

```bash
tsh> jobs
tsh> 
```

What happened?  Remember that `/bin/sleep 10` was _running_ in the
background.  When the program terminated, the shell took notice and removed
the job from the global array `jobs`, so when the built-in command `jobs` was
run, the job was no longer there.

Here is another example:

```bash
tsh> /bin/sleep 5 &
[1] (1791) /bin/sleep 5 &
tsh> /bin/sleep 20 &
[2] (1792) /bin/sleep 20 &
tsh> jobs
[1] (1791) Running /bin/sleep 5 &
[2] (1792) Running /bin/sleep 20 &
tsh> jobs
[2] (1792) Running /bin/sleep 20 &
tsh> jobs
tsh>
```

In this case:
 1. Two commands are entered, one immediately after the other, and a job is
    created and associated with the process for each, jobs 1 and 2,
    respectively.
 2. `jobs` is entered immediately, and both jobs show up in the list, each with
    their job ID (1 and 2) and process ID (1791 and 1792).
 3. After job 1 has terminated (i.e., 5 seconds has passed), `jobs` is entered,
    and only job 2 is still running.
 4. After all jobs have terminated (i.e., 20 seconds has passed), `jobs` is
    entered, and no jobs are still running.


### Non-Existent Commands

The shell is no dummy.  If you pass it a command that is neither the valid path
of an executable nor a built-in command, it will complain!

```bash
tsh> /does/not/exist
/does/not/exist: Command not found
```


### Recap 1

By this point, there should be an understanding of the following:
 - a "job" is simply the process(es) associated with a single command line
   given to the shell.
 - a job has a state, which is either _foreground_, _background_, or _stopped_.
   From `tsh.c`:
   ```c
   /* Job states */
   #define UNDEF 0 /* undefined */
   #define FG 1    /* running in foreground */
   #define BG 2    /* running in background */
   #define ST 3    /* stopped */
   ```
 - a command that does not use the `&` operator is started as a foreground job.
 - there is at most one foreground job.
 - a command that uses the `&` operator is started as a background job.
 - there may be one or more background jobs.


### Changing Job State

So far we have simply _started_ commands in either the foreground or the
background and let them run to completion.  But this shell can also change the
state of a job, _after_ it has started running.  A few examples follow.

To change the state of a foreground job to _stopped_, press `ctrl`+`z`:

```bash
tsh> /bin/sleep 20
^ZJob [1] (5376) stopped by signal 20
tsh> jobs
[1] (5376) Stopped /bin/sleep 20
tsh>
```

As long as the job is stopped, it is not scheduled to be run, not even in the
background.

To change the state of a stopped job to background, enter `bg` at the prompt,
followed by either a job ID (preceded by `%`) or a process ID:

```bash
tsh> bg %1
[1] (5376) /bin/sleep 20
tsh>
```

or:

```bash
tsh> bg 5376
[1] (5376) /bin/sleep 20
tsh>
```

In either case, the job is now _running_ again, though still only in the
background.

To change the state of a job from stopped or background to foreground, enter
`fg` at the prompt, followed by either a job ID (preceded by `%`) or a process
ID:

```bash
tsh> jobs
[1] (5376) Stopped /bin/sleep 20
tsh> fg %1
tsh>
```

or:

```bash
tsh> jobs
[1] (5376) Stopped /bin/sleep 20
tsh> fg 5376
tsh>
```

Assuming the job is allowed to run to completion without further interruption,
the prompt is not returned until the command completes.

If you try to pass an invalid (i.e., not associated with any current job) job
ID or process ID to `fg` or `bg`, the shell will complain!

```bash
tsh> fg %1
%1: No such job
tsh> fg 1234
(1234): No such process
tsh> bg %1
%1: No such job
tsh> bg 1234
(1234): No such process
tsh>
```

Finally, the shell will complain if your `fg` or `bg` command is missing a job
ID or process ID altogether:

```bash
tsh> fg
fg command requires PID or %jobid argument
tsh> bg
bg command requires PID or %jobid argument
tsh>
```

Note that, just like `jobs`, `bg` and `fg` are built-in commands, which will
result in code from your program being run.  Specifically, the `do_bgfg()` is
the function that will be called with `bg` or `fg` is entered.


### Recap 2

At this point, there should be an additional understanding of the following:
 - there may be one or more jobs that have state background or stopped.
 - the state of a foreground job can be changed by pressing `ctrl`+`z`.
 - the state of a background or stopped job can be changed by using `fg` or
   `bg` at the prompt.


### Interrupting Jobs

As we have seen pressing `ctrl`+`z` will change the state of a foreground job
to stopped.  If instead you want to terminate the process, try `ctrl`+`c`:

```bash
tsh> /bin/sleep 20
^CJob [1] (11830) terminated by signal 2
tsh>
```


### Detecting Job State Changes

As we have seen, among the ways a state of a job can be changed is by pressing
`ctrl`+`c` or `ctrl`+`z` while the job is in the foreground.  These each
effectively send a signal to the shell--which the shell passes along to the
processes associated with the job.  The process is then either terminated
or stopped, respectively.

However, the processes associated with shell jobs are still just processes, so
they can be signalled from outside the shell too, from other processes on the
system.  For example, suppose the following is run from the shell, and the
process associated with the foreground job has process ID 17311:

```bash
tsh> /bin/sleep 30
```

Now suppose the following is run from a different shell on the same system:

```bash
kill -INT 17311
```

The signal is sent directly to the process, not to the shell.  Yet the shell
detects that the process was sent an interrupt signal; back at the tiny shell,
the following is printed:

```bash
Job [1] (17311) terminated by signal 2
tsh>
```

Or if the following had been run:

```bash
$ kill -TSTP 17311
```

Then the following would have been printed:

```bash
Job [1] (18107) stopped by signal 20
tsh> 
```


### Terminating the Shell

The shell implements a "read/eval" loop which continues reading and evaluating
input forever--unless and until one of two things happens:
 - The following is entered at the prompt:
   ```bash
   tsh> quit
   ```
   `quit` is a built-in command, just like `jobs`, `fg`, and `bg`.  When `quit`
   is entered at the prompt, the shell simply calls `exit(0)`, upon which the
   process terminates immediately.
 - An end-of-file (EOF) indicator is received when the shell attempts to read
   input from standard input.  With a keyboard, an EOF can be sent with
   `ctrl`+`d`.  When EOF is detected, the shell also calls `exit(0)`,
   terminating the process.
Try either one of these to make the shell exit and to return to the shell from
which you called `./tshref`.


### Recap 3

At this point, there should be an additional understanding of the following:
 - Jobs can be interrupted by receiving signals in one of two ways:
   - Pressing `ctrl`+`z` or `ctrl`+`c` while a job is in the foreground sends a
     signal to the shell, which is, in turn, sent to the process group
     associated with the foreground job.
   - A process can use the `kill()` system call to send a signal directly to the
     process associated with a job.
 - Whichever method is used, the shell will detect that there was a change.
 - The shell will end when EOF is encountered or when the built-in command
   `quit` is entered on the command line.


## Functionality Not Included

While the tiny shell has a lot of nifty features, such as those demonstrated
previously, there are a few that are clearly missing, which are enumerated
here, for your reference:

 - Tiny shell does not perform any input or output redirection from or to
   files.
 - Tiny shell does not perform any pipelining between processes.
 - Tiny shell executes programs with an empty environment, so any command
   executed with tiny shell must be specified with an absolute path (e.g.,
   `/bin/cat` instead of `cat`).


## Your Tiny Shell

Run the following to compile `tsh.c`:

```bash
make
```

Run the incomplete tiny shell implementation derived from `tsh.c`:

```bash
./tsh
```

But you will note that it is not as responsive as the reference implementation:

```bash
tsh> /bin/echo foo bar
tsh> baz
tsh> quit  
tsh>
```

It _reads_ just fine, but it does not _evaluate_ anything, neither built-in
commands nor executable files.  That is because it is lacking the evaluation
functionality.  That is where you come in!


## `tsh.c` Overview


### Read/Eval Loop

The read/eval loop is in the `main()` function of `tsh.c`:

```c
    /* Execute the shell's read/eval loop */
    while (1) {
```

Within the `while` loop, you will see a `printf()` statement for the prompt
(`tsh>`), an `fgets()` statement that reads a line from standard input and
populates the string `cmdline`, and a check for EOF using `feof()`.  We have
already seen what happens when EOF is detected; however, when it is _not_ EOF,
then it calls `eval()`, passing `cmdline` as an argument.  That is the entire
read/eval loop.

`eval()` is pretty empty.  Let's start by just giving it a simple body:

```c
void eval(char *cmdline) 
{
    printf("You entered: %s\n", cmdline);
    return;
}
```

Now if you re-`make` and run the newly compiled `tsh`, you will get more
interesting output:

```bash
tsh> foo bar
You entered: foo bar

tsh>
```

This gives you an idea of what is being passed to `eval()`--a string (i.e.,
an array of `char`, terminated by a null byte).  But that single string needs
to be parsed and then evaluated.  Fortunately, there is a
[helper function](#parseline) to help you with the parsing.

Now make one last change, which will help you see how the program `strace`
might help you understand and troubleshoot your shell.  `strace` reports any
system calls that are made by a specified process, as well as signals received
by that process.  Modify your `eval()` function to fork a child process and
send a `SIGTERM` signal to that process, as follows:

```c
void eval(char *cmdline) 
{
    printf("You entered: %s\n", cmdline);
    pid_t pid = fork();
    if (pid > 0) {
        kill(pid, SIGTERM);
    }
}
```

Now enter the following at the command line:

```bash
strace -f ./tsh
```

You will see a bunch of output associated with system calls being made.  At the
very end you'll see `read(0, `.  That is the call to `read()` that is waiting
for data on standard input before it returns.  Enter "foo" at the prompt to get
the `eval()` code to be run.  You should see additional lines of output that
show: the call to `read()` returning; the `write()` call associated with
`printf()`; the `fork()` call (shows up as `clone()`); the `kill()` call issued
by the parent process; the `SIGTERM` call being received by the child process;
and the `SIGCHLD` call being received by the parent process.  The output is
quite a lot to take in, but you can also limit the system calls that `strace()`
prints out with something like this:

```bash
strace -f -e trace=clone,%signal ./tsh
```

This shows only the `clone()` (i.e., `fork()`) system call and any
signal-related activiy (including `kill()`).
See [Debugging Hints](#debugging-hints) for more.


### Signal Handlers

The functions `sigchld_handler()`, `sigtstp_handler()`, and `sigint_handler()`
are installed as signal handlers for the shell:

```c
    /* These are the ones you will need to implement */
    Signal(SIGINT,  sigint_handler);   /* ctrl-c */
    Signal(SIGTSTP, sigtstp_handler);  /* ctrl-z */
    Signal(SIGCHLD, sigchld_handler);  /* Terminated or stopped child */
```

Thus, whenever the shell receives a signal of type `SIGINT`, `SIGTSTP`, or
`SIGCHLD`, the respective handler will be called.  These handlers will be used
to manage the active jobs.  For example, when `ctrl`+`z` or `ctrl`+`c` is
entered on the keyboard while a foreground job is running, the shell receives
the `SIGTSTP` or `SIGINT`, respectively, and uses the handler to pass that
signal on to the process _group_ associated with the foreground job--so the
foreground job is stopped or interrupted, not the shell.

You will implement these handlers.


# Instructions

_This is where you start coding!_

Before you begin, _comment out_ the following line of code:

```c
    Signal(SIGINT,  sigint_handler);   /* ctrl-c */
```

As you are working on the first parts the lab, there will be times when it will
be desirable for you to interrupt your running shell, i.e., with `ctrl`+`c`.
Because the function `sigint_handler()` is currently empty, using it as the
handler for `SIGINT` will have the behavior of `SIGINT` being ignored.  This
might be confusing to you and can also be cumbersome to work around.
Commenting out the above line of code will therefore make development easier.
You will un-comment the line when you get the appropriate point in the lab.

Flesh out the following functions in `tsh.c` to create a shell that supports
command execution, signal handling, and job control.


## `builtin_cmd()`

`builtin_cmd()` takes the following as an argument:

 - `char **argv` - an array of strings representing a command and its arguments

Test the first string in the array.  If it matches one of the following, then
follow the corresponding instructions, and return 1.

 - `quit` - call `exit(0)`
 - `fg` or `bg` - call `do_bgfg()`, passing in `argv`, which is list of
   arguments parsed from the command-line input
   with [`parseline()`](#parseline)).
 - `jobs` - call `listjobs()`

If the first string in the array does not match any of these, then return 0--an
indicator that the command passed in was _not_ a built-in command.


## `eval()`

`eval()` takes the following as an argument:

 - `char *cmdline` - a string containing the contents of a command line read in
   from standard input in the read/eval loop.

Remove any code added for demonstration purposes.

Call the `parseline()` helper function,
[which has been implemented for you](#helper-functions).  Call `builtin_cmd()`
to see if the command line corresponds to a built-in command.  Otherwise, do
the following:
 - Block `SIGCHLD`, `SIGINT`, and `SIGTSTP` signals. (They will be unblocked
   after the `fork()` in both the parent and the child.)  The reason for adding
   this is to avoid a race condition.  If the child (created with a call to
   `fork()`) runs to completion before the parent has had a chance to add a job
   for it, then the parent will receive `SIGCHLD`, start executing
   `sigchld_handler()`, and attempt to delete a job that does not exist.
   Temporarily blocking `SIGCHLD` allows the parent to add the child before
   `SIGCHLD` can ever be received.
 - Fork a child process.
 - In the child process:
   - Unblock signals by restoring the mask.
   - Run the executable in the context of the child process using `execve()`.
   - If the command is invalid, then print an error and exit.  The error that
     you print should match the format of that printed by the reference shell
     in the same cirumstances.  See the [example](#non-existent-commands)
     above.
 - In the parent process:
   - Put the child process in its own process group, for which the group ID is
     the same as the process ID of the child process.  You can use
     `setpgid(pid, pid)`, where pid is the process ID of the child process.
     This makes it so that any signals sent to the group ID of the child
     process do not also go to the shell itself, which would effectively
     terminate the shell!
   - Add the job to the job list.
   - Unblock signals by restoring the mask.
   - If the job is to be run in the foreground (check the return value of
     `parseline()`), wait for the job to finish.  For now, you can simply use
     `waitpid()`.  However, eventually you will replace this with `waitfg()`,
     which you will soon implement.
   - Otherwise (background job), print out a string indicating that the job is
     in the background.


## Checkpoint 1

At this point, test your shell by 1) calling `make` to compile `tsh.c` and 2)
entering each of the following at the command line:

 - `/bin/sleep 10`
 - `/does/not/exist`
 - `quit`

They should work as expected.  See the [examples](#reference-tiny-shell).

You can also test your work with [automated testing](#automated-testing).
Tests 1 - 3 should work at this point.


## `sigchld_handler()`

`sigchld_handler()` is called every time a child process terminates normally,
exits due to an unhandled signal (e.g., `SIGINT`), or has stopped.  (i.e.,
`SIGTSTP`).

Start out by executing a simple print statement when `sigchld_handler()` is
entered:


```c
void sigchld_handler(int sig) 
{
	if (verbose)
		printf("sigchld_handler: entering\n");
	return;
}
```

Call `make` to compile `tsh.c`, then start the shell with the `-v` option.  Now
repeat the commands from [Checkpoint 1](#checkpoint-1).  They should work as
they did previously, but you should also see output from the print statement
that you just added when the process finishes.

`waitpid()` is the key function that you will utilize in `sigchld_handler()`.
Read the man page for `waitpid(2)` if you haven't already, and pay special
attention to the following:
 - the different options for the `pid` parameter;
 - the different options for the `options` parameter (note: multiple options
   can be specified by using the bitwise-OR `|` operator); and
 - the macros that can operate on the value of `status` after `waitpid()`
   returns.

Now do the following:

 - Call `waitpid()` such that it returns the process ID of _any_ child process
   that has _already_ terminated or stopped (see the `WUNTRACED` option). That
   is, it should not actually _wait_ on any child that is still running (see
   the `WNOHANG` flag), but simply return if there are no children that are
   ready (return value 0) or no children at all (return value negative).
   (See the "RETURN VALUE" section in the `waitpid(2)` man page.)
 - Loop until `waitpid()` cannot find any more child processes that are ready
   to be handled, i.e., return value is less than or equal to 0.  For each
   iteration of the loop:
   - If the child process has been stopped, then change the state of the
     corresponding job, and print out a message indicating that the job has
     been stopped.
   - If the child process terminated because of an uncaught signal (e.g.,
     `SIGINT`), then delete the job associated with the child process, and
     print a message indicating that the job has been terminated by a signal.
   - If the child process terminated normally (i.e., not because of a signal),
     then simply delete the job associated with the child process.

Note that calling `waitpid()` in a _loop_ is important because when
`sigchld_handler()` runs, it is possible that multiple children changed state,
and the kernel _sent_ `SIGCHLD` multiple times before it was received.  But
when `SIGCHLD` is _received_, it is only known that it was signalled _at least_
once.  The loop helps account for child processes that would have otherwise
gone unhandled.

Finally, note that `waitpid()` does not simply _identify_ processes that have
terminated or stopped, but also _reaps the resources_ of those that have
terminated.


## `waitfg()`

The purpose of `waitfg()` is to wait on a process for as long as it is in the
foreground.  Simply calling `waitpid()` is insufficient because the process
being waited on might change state, at which point it should no longer be
waited on.

`waitfg()` takes the following as an argument:

 - `pid_t pid` - an integer corresponding to the process ID of the process we
   are waiting on.

Implement a `sleep()` loop.  Call `sleep(1)` repeatedly as long as the job
with process ID `pid` is in the foreground (i.e., has state `FG`).

Now replace the `waitpid()` call that you added to `eval()` with a call to
`waitfg()`.


## Checkpoint 2

At this point, test your shell by 1) calling `make` to compile `tsh.c` and 2)
entering each of the following at the command line:

 - `/bin/sleep 10`
 - `/bin/sleep 10 &`
 - `quit`

Additionally, processes should be able to receive a signal from outside the
shell.  For example, when `/bin/sleep 10` is called, and `kill` is called with
`SIGINT` or `SIGTSTP`, then the following should be seen (respectively):

```bash
tsh> /bin/sleep 20
Job [1] (5355) terminated by signal 2
```

or:

```bash
tsh> /bin/sleep 20
Job [1] (5355) stopped by signal 20
```

They should work as expected.  See the [examples](#reference-tiny-shell) for
more.

You can also test your work with [automated testing](#automated-testing).
Tests 1 - 5 and 16 should work at this point.


## `sigint_handler()` and `sigtstp_handler()`

`sigint_handler()` or `sigtstp_handler()` is called every time a `ctrl`+`c` or
`ctrl`-`z` is entered at the keyboard, respectively.  Because the correct
behavior is not for the _shell_ to be interrupted or stopped, the job of the
handler is to pass on the signal to the process group associated with the
foreground job, if any.

Start out by executing a simple print statement when `sigint_handler()` is
entered:

```c
void sigint_handler(int sig) 
{
	if (verbose)
		printf("sigint_handler: entering\n");
	return;
}
```

Then do something similar for `sigtstp_handler()`.

Now _un-comment_ the line of code that installs the handler for `SIGINT` (i.e.,
the one you commented out before you began coding).:

```c
    Signal(SIGINT,  sigint_handler);   /* ctrl-c */
```

Now call `make` to compile `tsh.c`, then start the shell with the `-v` option.
Then repeat the commands from the [Changing Job State](#changing-job-state) or 
[Interrupting Jobs](#interrupting-jobs) sections that include the `ctrl`+`c` or
`ctrl`+`z` keystrokes.  The `ctrl`+`c` or `ctrl`+`z` keystrokes will not yet
have any effect on the foreground process, but you should see output from the
print statement when they are entered.

Now add the appropriate code for `sigint_handler()` and `sigtstp_handler()`,
such that the signal received is sent by the shell to the process group of the
foreground job, if any.


## Checkpoint 3

At this point, test your shell by 1) calling `make` to compile `tsh.c` and 2)
repeating the commands from the [Changing Job State](#changing-job-state) or 
[Interrupting Jobs](#interrupting-jobs) sections that include the `ctrl`+`c` or
`ctrl`+`z` keystrokes.  While you cannot yet use the `fg` and `bg` command to
put non-foreground (stopped or backgrounded) jobs in the foreground or
background, respectively, the `ctrl`+`c` or `ctrl`+`z` keystrokes should,
respectively, interrupt or stop a foreground process at this point.

You can also test your work with [automated testing](#automated-testing).
Tests 1 - 8, 11 - 12, and 16 should work at this point.


## `do_bgfg()`

`do_bgfg()` is called by `builtin_cmd()` when a command starting with `bg` or
`fg` is entered at the command line.  It takes the following as an argument:

 - `char **argv` - an array of strings representing a command and its arguments

Ensure that a command-line argument was passed to `bg` or `fg`; print an
error otherwise, using the format matching the [example](#changing-job-state)
above.  Examine the command-line argument passed to `bg` or `fg`, and determine
whether it is a job ID or a process ID that was specified (hint: look for the
`%`).  Determine whether the job ID or process ID corresponds to a valid job,
and print an error otherwise, using the format matching the
[examples](#changing-job-state).  If the job exists, then update its state.
Send a `SIGCONT` signal to the process group of the job.  Finally, if `fg` was
specified, then wait on the job in the same way that you did in `eval()`, i.e.,
with `waitfg()`.


## Final Checkpoint

At this point, test your shell by 1) calling `make` to compile `tsh.c` and 2)
entering commands from the [Changing Job State](#changing-job-state) or
sections that include the `bg` and `fg` commands.  Of course, the command
sequences from all previous checkpoints should still work as well.

You can also test your work with [automated testing](#automated-testing).
Tests 1 - 16 should work at this point.


# Helper Functions

The following function has been written to help you parse the command line.


## `parseline()`

`parseline()` finds all the words (i.e., non-whitespace characters separated by
whitespace) on the command line and puts them into an array of strings which
is passed in as an argument: `char **argv` (i.e., an array of `char *`).  It
returns true if the last word on the command line is the background operator,
`&`; false otherwise.  Thus, you can use the return value to determine whether
or not the job should start out in the background or foreground, respectively.

For example, suppose the following command line is provided to your shell:

```bash
/bin/cat test.txt
```

After calling `parseline()`, `argv` contains the following:

```c
argv[0] = "/bin/cat";
argv[1] = "test.txt";
argv[2] = NULL;
```

(A `NULL` value at index 2 indicates that that there are no more words, so your
code can detect that programmatically.)

In this case, `parseline()` will return `0` (false).  However, if the command
line had been the following:

```bash
/bin/cat test.txt &
```

Then `argv` would still contain the following after calling `parseline()`:

```c
argv[0] = "/bin/cat";
argv[1] = "test.txt";
argv[2] = NULL;
```

But `parseline()` would return `1` (true).


## Job Handling Functions

The following functions are used for manipulating the global array of job
structures (`struct job_t`), `jobs`:

 - `clearjob()` - clears the entries in a job struct
 - `maxjid()` - returns the largest allocated job ID
 - `addjob()` - adds a job to the job list
 - `deletejob()` - deletes a job with PID=pid from the job list
 - `fgpid()` - returns the PID of current foreground job, 0 if no such job
 - `getjobpid()` - finds a job (by PID) in the job list
 - `getjobjid()` - finds a job (by JID) in the job list
 - `pid2jid()` - maps a process ID to a job ID
 - `listjobs()` - prints the job list


# Debugging Hints

 - Place helpful print statements in your code, for debugging.  Even though
   your standard output is not redirected in this lab, printing to standard
   error (instead of standard output) is a good practice.  In this case, use
   `fprintf(stderr, ...)`.
 - If you are using VScode,
   [set up the debugger](../contrib/vscode-debugger/README.md), and use it to
   walk through your code.
 - Use the program `strace` to show you which system calls are being issued and
   which signals are being received.  `strace` can be used with various
   command-line options to cater it to your needs.  For example, the following
   command:

   ```bash
   strace -f -e trace=clone,%signal ./tsh
   ```

   calls `strace` on `./tsh`, showing only the `clone()` (i.e., `fork()`)
   system call and any signal-related activiy (including `kill()`).  The `-f`
   option indicates that child processes should be traced also, which is
   desirable since an important part of the shell is creating and managing
   child processes.  See the man page for `strace(1)` for more usage
   information.  Note that any calls to `fork()` will appear as `clone()` in
   `strace()` output.


# Automated Testing

The trace files provided can be used to test the behavior of your shell in an
automated fashion, with the help of the driver.  Each trace file contains a
brief description of the test, as well as a list of shell commands or other
directives to be used in testing.  For example, `trace16.txt` contains the
following:

```
#
# trace16.txt - Tests whether the shell can handle SIGTSTP and SIGINT
#     signals that come from other processes instead of the terminal.
#

/bin/echo tsh> ./mystop 2 
./mystop 2

SLEEP 3

/bin/echo tsh> jobs
jobs

/bin/echo tsh> ./myint 2 
./myint 2
```

In this case, the shell receives and evaluates the following two lines as
commands:

```
/bin/echo tsh> ./mystop 2 
./mystop 2
```

(Note that the first of each pair of commands in a trace file typically
involves the command `/bin/echo`, and its job is simply to print out the second
command. This makes the driver output a little easier to follow.)

The next line, `SLEEP 2`, is not actually a command, but rather a directive
that the driver should wait for 2 seconds before executing the next command, in
this case, `/bin/echo tsh> jobs`.  Other directives in trace files include
`INT` and `TSTP`, which direct the driver to send a `SIGINT` or a `SIGTSTP` to
the shell, simulating a `ctrl`+`c` or `ctrl`+`z`, respectively.

To run the _reference_ shell against the a `trace16.txt`, use the following:

```bash
make rtest16
```

Replace `rtest16` with `rtest01`, `rtest02`, etc., to test the reference shell
against `trace01.txt`, `trace02.txt`, etc.

Running the tiny shell against a trace file generates the same output you would
have gotten had you run your shell interactively (except for an initial comment
that identifies the trace and its description).  For example:

```bash
$ make rtest16
./sdriver.pl -t trace16.txt -s ./tshref -a "-p"
#
# trace16.txt - Tests whether the shell can handle SIGTSTP and SIGINT
#     signals that come from other processes instead of the terminal.
#
tsh> ./mystop 2
Job [1] (5041) stopped by signal 20
tsh> jobs
[1] (5041) Stopped ./mystop 2
tsh> ./myint 2
Job [2] (5045) terminated by signal 2
```

For comparison, to run _your_ shell against `trace16.txt`, run the following:

```bash
make stest16
```

By comparing the output of `make stest` with that of `make rtest`, you can see
how well your tiny shell did against the reference shell.  This can be
automated with:

```
make test16
```

(etc.)

Additonally, to run a comparison against _all_ traces, you can run the
following:

```
make testall
```

For example:

```
$ make testall
./checktsh.pl
Checking trace01.txt...
Checking trace02.txt...
Checking trace03.txt...
Checking trace04.txt...
Checking trace05.txt...
Checking trace06.txt...
Checking trace07.txt...
Checking trace08.txt...
Checking trace09.txt...
Checking trace10.txt...
Checking trace11.txt...
Checking trace12.txt...
Checking trace13.txt...
Checking trace14.txt...
Checking trace15.txt...
Checking trace16.txt...
```

Happy testing!


# Evaluation

Your code will be evaluated on one of the CS lab machines. It will be compiled
using `make` with the included `Makefile` and tested using `make testall`.

Your score will be computed out of a maximum of 100 points based on the
following distribution:

 - 96 points for correct shell behavior: 16 trace files at 6 points each.
 - 4 points for compilation without warnings


# Submission

Please copy your `tsh.c` file to one of the CS lab machines, and ensure your
file compiles and runs the tests as expected using `make` and `make testall`.

Upload `tsh.c` to the assignment page on LearningSuite.
