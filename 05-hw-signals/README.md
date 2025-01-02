# Signals

The purpose of this assignment is to give you hands-on experience with signals.
Code is provided that has handlers installed for various signals.  You will
interact with the existing code and change its behavior using the `kill()`
function.


# Maintain Your Repository

 Before beginning:
 - [Mirror the class repository](../01a-hw-private-repo-mirror), if you haven't
   already.
 - [Merge upstream changes](../01a-hw-private-repo-mirror#update-your-mirrored-repository-from-the-upstream)
   into your private repository.

 As you complete the assignment:
 - [Commit changes to your private repository](../01a-hw-private-repo-mirror#commit-and-push-local-changes-to-your-private-repo).


# Getting Started

This section is intended to familiarize you with the concepts associated with
this assignment and the resources provided to help you complete it, including
some simple examples of signal usage.  You will begin coding in the
[instructions](#instructions) section.


## Reading

Read the following in preparation for this assignment:
 - Section 8.5 in the book
 - The man pages for the following system calls:
   - `signal(7)`
   - `sigprocmask(2)`
   - `kill(2)`


## Resources Provided

 - `signals.c` - installs handlers for a number of signals, and runs a simple
   `sleep()` loop that is interrupted to handle reception of those signals.
 - `killer.c` - sends signals to its child process, which is running the code
   from `signals.c`.  This is where you will do your work!
 - `Makefile` - Compiles both executables by running `make`.


## Building the Binaries

Run the following to build the `signals` and `killer` executables:

```bash
make
```


## `signals.c` Overview

`signals` does the following:

 1. Installs signal handlers for various signals (`install_sig_handlers()`).
 2. Calls `fork()`:
    - The child calls `sleep_block_loop()`, which spins in a mostly uneventful
      `sleep()` loop for 20 seconds.  In addition to sleeping, it checks 
      the value of the variable `block` each iteration; if true (non-zero), it uses
      `sigprocmask()` to block `SIGINT` and `SIGCHLD`, otherwise, it unblocks
      `SIGINT` and `SIGCHLD`.  After the 20 seconds, it simply prints "25" on a
      line of its own.
    - The parent calls `start_killer()`, in which `execve()` is invoked to
      execute the executable passed in on the command line (`killer`), which
      then becomes the code for the parent process.


## `killer.c` Overview

`killer` takes two arguments on the command line:
 - `scenario` - an integer between 0 and 9, designating the specific scenario
   that should be run.
 - `pid` - an integer corresponding to the process ID of the child process,
   i.e., the one to which signals will be sent.

It then runs a `switch` statement with a `case` for every scenario. Each
scenario is supposed to yield a [specific output](#desired-output).  The code for
each scenario will be inserted into each corresponding `case` statement.


## Starter Commands

To demonstrate how things work, let's walk through an example.  First, run the following:

```bash
./signals ./killer 0
```

This will invoke the code corresponding to `case` "0", which is initially empty:
```c
	case '0':
		break;
```

That means that the `sleep()` will simply run uninterrupted.  After 20
seconds, you should see the following output:

```bash
25
```

Now look closer at the `sig_handler3()` function in `signals.c`:

```c
void sig_handler3(int signum) {
	printf("%d\n", foo); fflush(stdout);
}
```

This is just a normal function that takes an integer as a parameter.  However,
the following code installs `sig_handler3()` as a signal handler for `SIGTERM`.

```c
	sigact.sa_handler = sig_handler3;
	sigaction(SIGTERM, &sigact, NULL);
```

Modify the code in `case` "0" of `killer.c`, such that `SIGTERM` is sent to the
child immediately:

```c
	case '0':
		kill(pid, SIGTERM);
		sleep(1);
		break;
```

Re-`make` and then re-run the command:

```bash
make
./signals ./killer 0
```

You should now see the output associated with `sig_handler3()`--that is, the
value of `foo`!

```
-1
25
```


# Instructions

_This is where you start coding!_

For each of scenarios 0 through 9, flesh out the corresponding `case` statement
in `killer.c` to elicit the [desired output](#desired-output).  You may only
use two functions: `kill()` and `sleep()`.  The first argument to `kill()` will
always be `pid` (i.e., the process ID corresponding to the child process).  The
second argument will be an integer corresponding to a signal.  The `sleep()`
function is just used to help avoid race conditions, so you can reliably plan
on a statement in the code where the signal will be received.  A call to
`sleep()` for at _least_ one second will follow every call to `kill()`.

For example, the code for a scenario might look like this:

```c
kill(pid, SIGHUP);
sleep(6);
kill(pid, SIGQUIT);
sleep(1);
kill(pid, SIGHUP);
sleep(3);
```

(i.e., `kill()`, `sleep()`, `kill()`, `sleep()`, etc.)

The trick, of course, is to determine which signals to send and at what times to
get the desired output.  Look at the handlers closely to see what they do, and
practice what you know about signal behavior to send the right signals at the
right times.  Draw a timeline if it will help.

The one special case is `sig_handler7()`.  It appears as though it is just
changing a global variable.  But changing that global variable in the handler
results in `SIGINT` and `SIGCHLD` being blocked--or unblocked--in the main
loop.  While it might have been more intuitive to toggle the blocking of
`SIGINT` and `SIGCHLD` right in the handler, unfortunately the set of blocked
signals is overwritten (restored, actually) when a handler returns, and that
won't be helpful for the exercise at hand.  You are welcome to still think of
them as having been carried out right in the handler!

You are not allowed to send signals other than those for which handlers are
installed in `signals.c`.  In particular, you cannot use `SIGKILL`.

You may modify `signals.c` all you want with comments, print statements and
whatever you want, if it will help you.  In the end, you will just be uploading
your `killer.c`, and we will use a stock `signals.c` to test against.

If you are wondering where to start, take a look at `signals.c`.  Document
every signal handler, and be clear about what it does.  Start with the ones
that print something out.  Then work your way backwards, so you can determine
the steps that will take you to the necessary output.


## Desired Output

Here is the desired output for each scenario.

### Scenario 0
```
1
2
25
```

### Scenario 1
(No output)

### Scenario 2
```
1
2
```

### Scenario 3
Restriction: if `SIGINT` or `SIGHUP` are used, they must be sent before three
seconds have passed!
```
1
2
1
2
```

### Scenario 4
```
1
1
2
2
```

### Scenario 5
```
1
```

### Scenario 6
```
1
2
7
10
```

### Scenario 7
```
1
2
7
```

### Scenario 8
```
1
2
6
```

### Scenario 9
Restriction: you cannot use `SIGINT` or `SIGHUP` on this scenario!
```
8
9
1
2
```


# Helps

Remember the following about signals:

 - When a handler is already being run for a given signal that was received, a
   new instance of that same signal can be _sent_, but it will not be
   _received_ until the handler has finished running.
 - When a handler is already being run for a given signal that was received, if
   a _different_ signal is received, the current (first) handler will be interupted.
   The handler for the first signal will resume when the handler for the
   interrupting (second) signal has finished.
 - Assigning `SIG_DFL` as the "handler" for a given signal returns the signal
   to its default behavior (i.e., as if there was no handler installed).
 - The default behavior of `SIGCHLD` is to ignore; the default behavior of
   others, including `SIGTERM` and `SIGINT` is to terminate.  See the man page
   for `signal(7)` for more.

Also note that if a `sleep()` call is interrupted by the receipt of a signal,
it will not continue sleeping up to the designated time after the interruption.
Instead, it will return "the number of seconds left to sleep," as per the
`sleep(3)` man page.  This should not affect the timing of your calls to
`kill()` and `sleep()`, but you might be surprised about the time taken to
complete a given scenario without this knowledge.


# Automated Testing

For your convenience, a script is also provided for automated testing.  This is
not a replacement for manual testing but can be used as a sanity check.  You
can use it by simply running the following:

```bash
./driver.py
```


## Submission

Upload `killer.c` to the assignment page on LearningSuite.
