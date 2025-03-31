# OpenMP

The purpose of this assignment is to give you hands-on experience with parallel
computation using threads and the OpenMP library.  Code is provided for
computing the Mandelbrot set.  You will parallelize this code using OpenMP and
demonstrate the efficiency by measuring the computation.


# Maintain Your Repository

 Before beginning:
 - [Mirror the class repository](../01a-hw-private-repo-mirror), if you haven't
   already.
 - [Merge upstream changes](../01a-hw-private-repo-mirror#update-your-mirrored-repository-from-the-upstream)
   into your private repository.

 As you complete the assignment:
 - [Commit changes to your private repository](../01a-hw-private-repo-mirror#commit-and-push-local-changes-to-your-private-repo).


# Preparation

Read the following in preparation for this assignment:
 - Sections 1.9.1 - 1.9.2 and 12.6 in the book
 - LLNL's [OpenMP Tutorial](https://hpc-tutorials.llnl.gov/openmp/)
 - Introduction in the header comments of `mandelbrot.c`.

Using the guidance from the [remote access information
page](../REMOTE_ACCESS.md), log in to a CS lab machine.

The exercises in this assignment will only work if run from a CS lab
machine.


# Instructions

The code in `mandelbrot.c` consists of three nested `for` loops, in which
computations are carried out, followed by two nested `for` loops in which the
computations are saved to an image file.  The outer-most loop in which the
computations are made can be parallelized, which will help reduce computation
time when multiple threads are used on multiple cores.  You will use OpenMP to
create this parallelization.  The second loop makes parallelization of the
first possible; if the points were written to the file *as they were
generated*, then all threads would be writing to the file concurrently, and the
file would be out of order.


## Part 1 - Getting Started

Run the following to compile `mandelbrot.c` without compiler optimization
(i.e., without the `-O` option):

```bash
gcc -o mandelbrot mandelbrot.c
```

Now execute the command to build the Mandelbrot set with the following:

```bash
./mandelbrot 0.27085 0.27100 0.004640 0.004810 1000 8192 pic.ppm
```

NOTE: This creates a very large file, `pic.ppm`, which you will be instructed
to delete later in the assignment, after you are done with it.

Run the following to get the SHA1 sum of the file:

```bash
sha1sum pic.ppm
```

Save the value of the SHA1 sum shown in the output.  Hint: it should start with
"04c0e2...".  You will be referring to it later, to make sure that your program
is still behaving properly after parallelizing it.

Normalize, and convert the output to png format using `convert` (part of the
ImageMagick suite):

```bash
MAGICK_CONFIGURE_PATH=. convert -negate -normalize -fill blue -tint 100 pic.ppm pic.png
```

(Note: setting the `MAGICK_CONFIGURE_PATH` environment variable communicates to
`convert` the directory in which it should look for `policy.xml`, which
contains the maximum resource values.  In particular, by using a custom version
of `policy.xml` in the current directory (`.`), we can override the system-wide
setting 256MiB of memory that `convert` can use to 2GiB.)

Finally, open `pic.png` in a Web browser or image viewer to see it.


## Part 2 - Parallelize Using OpenMP

Use OpenMP to parallelize the outer `for` loop in which the computations are
made.  You will need to apply the `parallel` and `for` directives to make it
work properly.  See the
[OpenMP Tutorial](https://hpc-tutorials.llnl.gov/openmp/do_for_directive/) for
more information.  Note that proper use of the `private()` clause is essential
for correct output and timing.  Think carefully about which variables (if any)
should be shared across threads and which need only be used locally.

Compile your program with `-fopenmp`:

```bash
gcc -o mandelbrot mandelbrot.c -fopenmp
```

Now use the
[`OMP_NUM_THREADS` environment variable](https://hpc-tutorials.llnl.gov/openmp/env_vars/)
to run your execution with 1 thread, then 2 threads.  For example:

```bash
OMP_NUM_THREADS=1 ./mandelbrot 0.27085 0.27100 0.004640 0.004810 1000 8192 pic.ppm
```

In both cases (1 and 2 threads), make sure the SHA1 sum of the file is the same
as that you computed in the previous section.

Now use the `time` command to run the program again, so you can see the total
_elapsed_ time (i.e., "wall clock time").

```bash
OMP_NUM_THREADS=1 time ./mandelbrot 0.27085 0.27100 0.004640 0.004810 1000 8192 pic.ppm
```

Note that `time` also shows the amount of "user" time, which is the sum total
of time spent processing in user mode, and "system" time, which is the sum
total of time spent processing in kernel mode on behalf of the process--both
across all cores.

When you run it with 1 thread, you should expect the elapsed time to be about
35 seconds, and with 2 threads, about 22 seconds.  There will be some variance,
but it should only be within a second or two.

Note that even though _elapsed_ time will have decreased, there should be
little variance between the two runs with regard to _user_ time.  This is
because if <code>T<sub>1</sub></code> is divided across each `p` threads, then
each spends approximately <code>T<sub>1</sub>/p</code> time processing, the sum
total of which is still <code>T<sub>1</sub></code>.  That being said, the user
time should always be around 30 seconds.


## Part 3 - Measure and Record Compute Times

Use the
[`omp_get_wtime()` function](https://hpc-tutorials.llnl.gov/openmp/omp_get_wtime/)
to measure the "wall clock" time required to carry out the first `for` loop
(i.e., the one that is parallelized).  When the `for` loop has finished, print
out the number of seconds required to compute the loop (in seconds).
Re-compile, and make sure that it runs properly.

Now use the `time` command to run the program again, so you can compare the
elapsed time for only the parallelized part of your program, with the total
elapsed time for your program.

```bash
OMP_NUM_THREADS=1 time ./mandelbrot 0.27085 0.27100 0.004640 0.004810 1000 8192 pic.ppm
```

The amount of time spent on the parallel part of your program should be a
significant fraction (more than half) of the total elapsed time.

Now execute your code for the following numbers of threads:
 - 1
 - 2
 - 4
 - 8
 - 16
 - 32

While your command is running, run the `top` command in another window *on the
same machine* to see that your program is not competing with any others for
time on the CPU.

For each run, record both:
 - the elapsed time for *only the parallel region* (i.e., the output from your
   program); and
 - the elapsed time for the entire program execution (i.e., "elapsed time"
   from `time` output)


## Part 4 - Questions

 1. How many cores are available for computation on your machine?  Hint: run:
    ```bash
    cat /proc/cpuinfo | grep ^proc | wc -l
    ```

 2. What happens to the time associated with computation of *only the parallel
    region* (i.e., the first `for` loop) as the number of threads doubles?

 3. What is the speedup (`α`) of the *only the parallel region* (i.e., the
    first `for` loop) when four threads are used?  Hint: calculate
    <code>S<sub>p</sub></code> for just the parallel region, with `p` = 4.

 4. At what point (i.e., how many threads) did you stop observing the expected
    performance gain in the parallel region of the code?

 5. At the point you indicated in question 4, what was the reason for the lack
    of additional performance gain?

 6. What is the *overall* speedup when four threads are used?  Hint: calculate
    <code>S<sub>p</sub></code> for the overall execution time of the program
    (i.e., using the "elapsed time" output by `time`), with `p` = 4.  Show the
    steps you used to calculate it.

 7. Using the result from question 6, compute the efficiency
    (<code>E<sub>p</sub></code>) of using four cores (i.e., `p` = 4) to
    parallelize with respect to *overall* execution time.  Show the steps you
    used to calculate it.

 8. Briefly explain why the efficiency calculated in query 7 is less than 1.

 9. Consider Amdahl's Law:

    <code>T<sub>α</sub> = pT/α + (1-p)T</code>

    In this case `α` is speedup of the parallel region only, and `p` is the
    fraction of original run time that is parallelizable.

    Find the fraction of parallelizable code, `p`, by using:
    - the answer to question 3, `α` (speedup of parallel region);
    - the "elapsed time" output by `time` for 4 threads as
      <code>T<sub>α</sub></code>; and
    - the "elapsed time" output by `time` for 1 thread as `T`.

 10. Using the result from question 9, as the number of threads grows
     indefinitely (`α` approaches infinity), what does
     <code>T<sub>α</sub></code> approach?

     For the purposes of this problem, assume that the non-parallel region does
     not vary with `α`.

# Cleanup

Remove `pic.ppm` and `pic.png` from your filesystem:

```bash
rm -f pic.ppm pic.png
```
