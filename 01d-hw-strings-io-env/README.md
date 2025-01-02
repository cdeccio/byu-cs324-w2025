# Strings, I/O, and Environment

The purpose of this assignment is to help you better understand strings, I/O,
and environment in C with a series of hands-on exercises.  You will flesh out
sections of an existing C program and answer questions about its output.


# Preparation

Read the following in preparation for this assignment:

 - 10.1 - 10.4 and 10.9 in the book

Additionally, man pages for the following are also referenced throughout the
assignment:

 - `write(2)`
 - `charsets(7)`
 - `ascii(7)`
 - `printf(3)`
 - `fprintf(3)`
 - `strcmp(3)`
 - `memcmp(3)`
 - `memset(3)`
 - `strcpy(3)`
 - `sprintf(3)`
 - `stdin(3)`
 - `stdout(3)`
 - `stderr(3)`
 - `fileno(3)`
 - `open(2)`
 - `read(2)`
 - `close(2)`
 - `getenv(3)`


# Instructions

This file contains questions divided into seven parts, beginning with an
[introduction](#introduction---characters-encoding-and-presentation)
and followed by parts
[1](#part-1---arrays-strings-pointers-and-memory-allocation) through
[6](#part-6---getting-and-setting-environment-variables).
The instructions in each part provide exercises for learning about memory
allocation, strings, I/O, and environment variables in C.  The file `learn_c.c`
contains a function corresponding to each part, in which you will do the
specified work for each question.

Follow the instructions for and answer each question.  For most questions, you
will re-compile and re-run the program using the following commands:

```bash
gcc -Wall -Wno-unused-variable -o learn_c learn_c.c
./learn_c test.txt
```

`gcc` is the GNU compiler collection, the C compiler that will be used.  The
`-o` option designates the name of the binary file resulting from compilation.
The combined options `-Wall -Wno-unused-variable` mean to show all compilation
warnings, _except_ warnings associated with unused variables.

Note that several exercises will have you modify the command line that you use
to get different results.

All of the exercises and questions are supposed to be taken at face value.
They might seem a little too straight-forward, but the point is to teach you
the concepts in a simple, hands-on way.  Important concepts include where a
variable lives and the content it refers to, either directly (e.g., an integer)
or indirectly (a pointer).


# Introduction - Characters, Encoding, and Presentation

Here is very brief lesson on characters, encoding, and presentation.


## ASCII

All char/byte values in C are simply 8-bit integers.  It is the interpretation
and presentation of those integer values according to some character set that
makes them "readable" characters.  For example, byte values less than 128
(i.e., without the most significant bit set) can be interpreted as part of the
American Standard Code for Information Interchange (ASCII) character set, which
includes the upper- and lower-case letters (A-Z and a-z), numbers (0-9),
punctuation, and more.  If these byte values are sent to the terminal, or any
other application that understands them to be ASCII, then it will print out the
ASCII equivalents.  For example, the following array of bytes:

```c
char s1[] = { 0x68, 0x65, 0x6c, 0x6c, 0x6f, 0x0a };
```

together represent the ASCII values: `'h'`, `'e'`, `'l'`, `'l'`, `'o'`, `'\n'`
(newline).

You can send these bytes to the terminal using the `write()` function, and the
terminal will display them as their corresponding ASCII values.

```c
write(STDOUT_FILENO, s1, 6);
```

(More will be explained about the `write()` system call later on.  For now,
just know that this system call sends these bytes to the terminal.)


## Beyond ASCII: Unicode

Here is a bit of bonus information related the limitations of ASCII and how
they are addressed.

ASCII has limitations in that it only supports 127 unique characters
(2<sup>7</sup> - 1).  Thus, other character sets have been developed, the most
widely used of which is Unicode.  Unicode has the ambitious goal of having a
mapping for "every character in every human language" (man page for
`charsets(7)`).  ASCII is a subset of Unicode: if a byte value is less than 128,
then it is ASCII, but if it greater, then it is encoded for Unicode,
typically using a byte encoding called UTF-8.  For example, the following array
of six bytes together represent the two simplified Chinese characters that mean
"Taiwan", followed by an (ASCII) newline:

```c
char s2[] = { 0xe5, 0x8f, 0xb0, 0xe7, 0x81, 0xa3, 0x0a };
```

Again you can send these bytes to the terminal using the `write()` function,
and the terminal will display them as their corresponding unicode characters.

```c
write(STDOUT_FILENO, s2, 7);
```

Finally, take a look at the presentation of the following sequence of
UTF-8-encoded Unicode characters:

```c
char s3[] = { 0xf0, 0x9f, 0x98, 0x82, 0x0a };
write(STDOUT_FILENO, s3, 5);
```

Yup, that is a "joy" emoji.  Not exactly "human language", but you get the
idea.  If it doesn't display in the terminal, try copying it and pasting it in
another application that has the proper support to display it.

For more information, see the man pages for `charsets(7)` and `ascii(7)`.


## `printf()` and Friends

What do `printf()` and `fprintf()` do?  They are similar to `write()`, but with
some important differences:
 - First, `printf()` and `fprintf()` operate on file streams (`FILE *`), which
   include user-level buffering.  That simply means that they "save up"
   `write()` calls and send the pending bytes only when it's most efficient to
   do so.  This is like going to the grocery store only when you need a whole
   week's worth of groceries instead of going there when you just need a single
   food item.
 - Second, instead of explicitly setting the number of bytes to send,
   `printf()` and `fprintf()` know when to stop sending bytes when they detect
   a null byte value (integer value 0), which you will see in this assignment.
 - Third, and most importantly for now, they perform "replacements" before
   calling `write()` on the resulting string.  For example, the `s` (e.g.,
   `"%s"`) conversion specifier indicates that it should be replaced by the
   null-terminated string specified.  The `x` and `d` conversion specifiers
   indicate that they should be replaced with the hexadecimal and decimal
   representations (in ASCII characters) of an integer, respectively.

   For example, consider the following statement:

   ```c
   printf("hello %d\n", 42);
   ```

   Before the string is written to the terminal, the substring "%d" (i.e., the
   two characters `'%'` and `'d'`) are replaced with the two byte values that
   comprise the string "42": 52 and 50 (decimal), 0x34 and 0x32 (hexadecimal),
   or `'4'` and `'2'` (ASCII).  The resulting string that is printed is:
   "hello 42\n".

   You can learn more about the available conversion specifiers on the man page
   for `printf(3)`.

The following snippets all yield equivalent results:

```c
printf("hello %d\n", 42);
```

```c
fprintf(stdout, "hello %d\n", 42);
```

```c
write(STDOUT_FILENO, "hello 42\n", 9);
```

(Note, however, that `write()` does not have buffering.  You will learn more
about buffering later in the assignment.)

Specifically, what is sent to the console in each case is the following
sequence of bytes/characters:

| Representation | | | | | | | | | |
| ---------------|-|-|-|-|-|-|-|-|-|
| Hexadecimal | 0x68 | 0x65 | 0x6c | 0x6c | 0x6f | 0x20 | 0x34 | 0x32 | 0x0a |
| Decimal | 104 | 101 | 108 | 108 | 111 | 32 | 52 | 50 | 10 |
| ASCII | `'h'` | `'e'` | `'l'` | `'l'` | `'o'` | `' '` | `'4'` | `'2'` | `'\n'` |

Again, see the man pages for `charsets(7)` and `ascii(7)`.  And you will see more
examples of this later in the assignment.


## Summary and Main Points

While you will get more hands on with `printf()` and friends in the exercises
that follow, the most important things to remember are:

 - Text is really just a bunch of integer values that an application (e.g., a
   terminal) knows how to interpret and present a certain way--i.e., as text.
 - `printf()` and friends can be used to format text for it to be presented.


# Part 1 - Arrays, Strings, Pointers, and Memory Allocation

In this section, you will perform some hands-on exercises to better understand
allocation of memory for arrays, strings, and pointers, both on the stack and
on the heap.  You will also learn about the compile-time operator `sizeof()`
and observe the effects of `malloc()` and `free()` using `valgrind`.

Remember that each question corresponds to a portion of code, each marked by a
comment in `learn_c.c`.  Each part also corresponds to a function in
`learn_c.c`.  You are expected to edit and/or add to the code for each question
unless the question's comment states that "no code changes" are required.

 1. `s1` is allocated on the stack.  Find the number of bytes/characters
    allocated on the stack for `s1` using the `sizeof()` operator (not
    `strlen()`!).  Note that `sizeof()` is a _compile-time_ operator; that
    means that the size (i.e., the number of bytes allocated) is determined at
    compile time, before the code ever runs.  In this case, `sizeof()`
    accurately reflects the number of bytes allocated for (i.e., the "size" of)
    `s1`, only because `s1` is explicitly assigned a value using a string
    literal.  (See questions 6 and 7 for counter examples, in which pointers
    are used.)

    Save the value as `s1_len`, and then print `s1_len` on a line by itself,
    using `printf()`.

    *How does the number of bytes allocated for `s1` compare to the number of
    visible characters pointed to by `s1`?*

 2. `memprint()` is a function defined right in `learn_c.c`.  It simply prints
    the contents of an array of type `char []`, byte-by-byte, to standard
    output using the designated format.

    Call `memprint()` on `s1` three times, passing `s1_len` as `len` each time.
    The first time, show each byte/character value as hexadecimal (i.e., format
    `"%02x"`).  The second time, show each byte/character value as decimal
    (i.e., format `"%d"`).  Finally, show each byte/character value as its
    corresponding ASCII character (i.e., format `"%c"`).

    *What is the (integer) value of the "extra" byte allocated for `s1`?*
    (That byte value is the very definition of what makes `s1` a "string" in
    C.)

 3. *What is the ASCII character associated with the hexadecimal value 0x23?*
    (Hint: See the man page for `ascii(7)`.)

 4. *What is the hexadecimal value of the ASCII character `z` (lower case)?*
    (Hint: See the man page for `ascii(7)`.)

 5. `s2` is also allocated on the stack.  Find the number of bytes/characters
    allocated on the stack for `s2` using the same methodology as you used for
    question 1.  Note that although an initial value is not explicitly assigned
    to `s2`, as it is with `s1`, the size of the array is explicitly given, so
    `sizeof()` can again be used.

    Save that value as `s2_len`, and then print `s2_len` on a line by itself,
    using `printf()`.

    *How does the number of bytes allocated for `s2` compare to the declared
    number of bytes for `s2`?*

 6. `s3` is a pointer, and the bytes associated with its value (i.e., the
    bytes that contain the address it refers to) are also allocated on the
    stack.  Because it is assigned the address of `s1`, it also happens to
    refer to bytes on the stack (i.e., because it now refers to the same bytes
    as `s1`).  However, even though the size of the array it refers to in this
    example is known, in a real scenario, it might point to anything, and there
    is no way at compile-time for that to be known.

    Save the value returned from `sizeof()` as `s3_len`, and then print
    `s3_len` on a line by itself, using `printf()`.

    *How does the number of bytes pointed to by `s3` compare to the output of
    `sizeof()`?  Briefly explain your answer.* (Hint: Memory addresses on an
    x86-64 system are 64 bits long.)

 7. `s4` is a pointer, and the bytes associated with its value (i.e., the
    bytes that contain the address it refers to) is also allocated on the
    stack.  Because it is assigned the return value of `malloc()`, it refers to
    bytes allocated on the heap.  Even though the values in this example are
    hard-coded, in a real scenario, the number value might be arbitrary (e.g.,
    could be the value of a variable); in either case, the bytes are not
    allocated until run-time.  Use the `sizeof()` operator against `s4`.

    Save the value returned from `sizeof()` as `s4_len`, and then print
    `s4_len` on a line by itself, using `printf()`.

    *How does the number of bytes pointed to by `s4` compare to the output of
    `sizeof()`?  Briefly explain your answer.* (Hint: Memory addresses on an
    x86-64 system are 64 bits long.)

 8. Run the program with `valgrind`:

    ```
    valgrind ./learn_c test.txt
    ```

    *How many bytes are "in use" at exit?  In other words, how many have been
    allocated on the heap with `malloc()` but not `free()`d?*

    Note that `valgrind` reports `malloc()`'d bytes that were not explicitly
    `free()`'d by the program itself, but the heap and all bytes allocated
    thereon are freed by the kernel when the program exits.  Thus, while
    calling `free()` explicitly is good practice and especially important for
    long-running programs, `malloc()`'d bytes will not consume resources beyond
    the lifetime of the program runtime.

 9. Immediately after printing out the return value of `sizeof()` for `s4`, use
    `free()` to de-allocate the memory associated with `s4`.  Run the following
    again:

    ```
    valgrind ./learn_c test.txt
    ```

    *How many bytes are "in use" at exit?  In other words, how many have been
    allocated on the heap with `malloc()` but not `free()`d?*


## Summary and Main Points

 - Bytes for strings and arrays of arbitrary byte value can be allocated on the
   stack or on the heap.
 - Bytes are allocated differently depending on how the variables are declared.
 - `sizeof()` is a compile-time operator.
 - Bytes allocated with `malloc()` continue to consume system resources until
   `free()` is called or the program exits.


# Part 2 - Arrays, Strings, Pointers, and Shared Content

In this section, you will perform some hands-on exercises to better understand
how arrays, strings, and pointers are used by the compiler to reference the
content they refer to, whether on the stack or on the heap.

Some of the questions that follow might feel similar, like the same thing is
being asked multiple times.  For this reason, we start with a brief
introduction.  Let's say the memory for the call frame for a given function
(e.g., `part2()`) is organized something like this:

Variable | Type | Variable Address | Address Referred To
---------|------|------------------|-------------------
`s1` | `char []` | addr1 (`&s1`) | `&s1[0]`
`s2` | `char []` | addr2 (`&s2`) | `&s2[0]`
`s3` | `char *` | addr3 (`&s3`) | `&s3[0]`

What this means is that each variable is stored at a given address on the
stack, denoted by "addr1", "addr2", etc.  These addresses can be found with the
code `&s1`, `&s2`, etc.  When any of these variables (`s1`, `s2`, etc.) is used
in your code, the bytes ultimately _referred to_ might be at the same address
as the variable itself or somewhere else, depending on the type of the
variable.  This is explained further in Question 11.  These referred-to
addresses can be found with the code `&s1[0]`, `&s2[0]`, etc.  All that being
said:

 - Question 10 is about comparing addr1 (`&s1`) to addr2 (`&s2`), etc.
 - Question 11 is about comparing `&s1[0]` to addr1, `&s2[0]` to addr2, etc.
 - Question 12 is about comparing `&s1[0]` to `&s2[0]`, etc.

 10. Print out the address (i.e., using the `&` operator) of each of the
     variables `s1`, `s2`, and `s3`, as a long unsigned integer in decimal
     format (i.e., format `"%lu"`), each on its own line.

     The C compiler will complain that you are passing `char *` where a
     `long unsigned int` was expected.  Usually that means that you are doing
     something wrong!  For this exercise, you can tell the compiler to simply
     treat the value like a `long unsigned int` by explicitly type-casting it
     as such.  To do so, preface it with `(long unsigned int)`.  Please note
     that this does not change anything with regard to the _value_ of the
     pointer; it merely tells the compiler that you are using it differently.

     Note that this exercise has nothing to do with the actual _value_ of the
     variables, which will be compared in a subsequent question.  Rather, this
     only has to do with the memory addresses of the variables themselves.

     *Which of the variables have the same address on the stack?  If so, which
     and why?*

 11. Print out the address _referred to_ by (i.e., the pointer _value_ of) each
     of the variables `s1`, `s2`, and `s3` as a long unsigned integer in
     decimal format (i.e., format `"%lu"`), each on its own line.  Since all
     these variables refer to arrays/strings, you can also think of each
     referred-to address as the address of the _first byte/character_ in each
     array/string referred to.

     See the comment on type casting from question 10.

     Note that while `s1`, `s2`, and `s3` are _declared_ differently, they
     effectively act the same, in that:

     - When represented as a (long unsigned)  _integer_ value (i.e., format
       `"%lu"`), `printf()` uses the referred-to address (i.e., the _pointer
       value_) as a replacement.
     - When represented as a _string_ value (i.e., format `"%s"`), `printf()`
       uses the values _at_ the referred-to address (i.e., the string contents)
       as a replacement.

     However, one difference between `char[]` and `char *` is that for
     `char[]`, the address of the variable is _also_ the address _referred to_
     by the variable.  That means that you cannot change the _referred-to
     address_ (or _pointer value_) of a variable declared `char[]`.

     *For which of the variables is the referred-to address (i.e., the pointer
     value) the same as the _address_ of the variable itself (i.e., the output
     associated with question 10)?  Briefly explain.*  (Hint: See explanatory
     text in this question.)

 12. *Which of the variables reference the same content?  That is, which of the
     referred-to addresses / pointer values are the same between `s1`, `s2`,
     and/or `s3`?  Briefly explain.*

 13. Use `printf()` to print out the contents of each of the array/string
     variables `s1`, `s2`, and `s3`, i.e., using the `"%s"` format, each on its
     own line.

     *Which arrays/strings have equal content and why?*

 14. Compare the following pairs of pointer values using the equality operator,
     `==`: `s1` and `s2`; `s1` and `s3`; `s2` and `s3`.  In each case, print
     the string "s1 == s2" (replacing the variable names for each pair, as
     appropriate) the conditional is true, indicating that the pointer values
     are equal.

     The C compiler will warn that you are comparing two pointer values and
     that the more deliberate way to do this is to compare the addresses
     of the _first byte/character_ in each array/string referred to.  This is
     true!  And if that warning is heeded (and the code is changed), then it
     will be clearer to you and anyone else looking at the code that it is not
     _content_ being compared but rather addresses. And that is the entire
     point of this exercise.  Thus, `s1 == s2` is equivalent to
     `&s1[0] == &s2[0]`, but the latter is more explicit.

     *Which arrays/strings have the same pointer values (i.e., refer to the
     same memory locations) and why?*

 15. Compare the values of the strings referenced by the following pairs of
     pointers, using the `strcmp()` function: `s1` and `s2`; `s1` and
     `s3`; `s2` and `s3`.  In each case, print the string "s1 == s2"
     (replacing the variable names for each pair, as appropriate) on its own
     line if the return value of `strcmp()` is 0, indicating that the string
     values are equal.

     *Based on the output, which arrays/strings have equal content (i.e.,
     the values of the bytes they point to are the same) and why?* (Hint: Your
     answer should be consistent with the answer for question 13).

 16. Note the existing code placed at the start of question 16. Now repeat the
     instructions for question 13.

     *For which arrays/strings has the content changed from question 13,
     and why?*

 17. Repeat the instructions for question 14.

     *Has the equivalence of pointer values changed from question 14?  Why or
     why not?*

 18. Repeat the instructions for question 15.

     *Has the equivalence of content changed from question 15?  Why or why
     not?*


## Summary and Main Points

Pointers (including strings) can be referenced and compared in several ways:

 - Address of content (i.e., pointer value), e.g., `s1 == s2`
 - Referenced content (i.e., bytes corresponding to pointer value)
   - As arbitrary bytes, e.g., `memcmp()`
   - As a null-terminated string of non-null characters, e.g., `strcmp()`


# Part 3 - Equivalence of Byte Values Using Different Representations

 19. Compare the values of the bytes referenced by the following pairs of
     pointers, using the `memcmp()` function (not `strcmp()`!):
     `s1` and `s2`; `s1` and `s3`; `s2` and `s3`.  In each case, print
     the string "s1 == s2" (replacing the variable names for each pair, as
     appropriate) on its own line if the return value of `memcmp()` is 0,
     indicating that the values of the compared bytes are equal.

     *Which arrays/strings have the same content and why?* (Hint: See both the
     [introduction section](#ascii) and questions 2 through 4.)


## Summary and Main Points

Bytes can be represented in different ways, even if their values do not change.


# Part 4 - String Comparison

In this section, you will perform some hands-on exercises to better understand
how to compare and copy both strings and arrays of arbitrary values in C.

 20. Compare the values of the bytes referenced by pointers `s1` and `s2`,
     using the `memcmp()` function (not `strcmp()`!).  Print the string "s1 == s2"
     on a line by itself if the return value of `memcmp()` is 0, indicating
     that the values of the compared bytes are equal.

     *Does `memcmp()` indicate that the arrays have the same content?  Why
     or why not?*

 21. Compare the values of the bytes referenced by pointers `s1` and `s2`,
     using the `strcmp()` function (not `memcmp()`!).  Print the string
     "s1 == s2" on a line by itself if the return value of `strcmp()` is 0,
     indicating that the string values are equal.

     *Does `strcmp()` indicate that the arrays have the same content?  Why
     or why not?*

 22. Use `memset()` to initialize every byte value in `s3` to `'z'` (or,
     equivalently, `0x7a`).  Then call `memprint()` on `s3` to show the
     hexadecimal value of each byte/character (i.e., format `"%02x"`).

     Repeat both the `memset()` function and the `memprint()` function for
     `s4`.

     *Does the output show any characters other than (ASCII) `z`?* (Hint: It
     shouldn't.)

 23. Use the `strcpy()` function (not `memcpy()`!) to copy the contents of `s1`
     to `s3`.  Then call `memprint()` on `s3` to show each byte/character value
     in the array as hexadecimal (i.e., format `"%02x"`).

     *Which bytes/characters were copied over from `s1`, including any null
     characters?*

 24. Use the `sprintf()` function to replace the contents of `s4`.  Use the
     format string `"%s %d\n"` and the values of `s1` and `myval`. Then call
     `memprint()` on `s4` to show each byte/character value in the array as
     hexadecimal (i.e., format `"%02x"`).

     *In which place(s) of the array was a null value placed?*

 25. *Which variables could be _appropriately_ used in place of `VAR` in the
     following code:*

     ```c
     memprint(VAR, "%02x", 8);
     ```

     Remember that `memprint()` prints arbitrary byte values, so it doesn't
     care _what_ the values are.  But it does care whether or not it can _find_
     the values (i.e., with a valid address).  So the addresses should
     explicitly refer to memory that has been populated with values to be read
     or memory that can be written to.  You are encouraged to experiment
     with this by actually calling `memprint()`.

     Hint: Note the compiler warnings.  Also, see explanatory text in
     question 11.


## Summary and Main Points

String comparison differs from arbitrary byte comparison in the following ways:

 - String comparison with `strcmp()` compares strings byte-by-byte until a null
   character is encountered;
 - Byte comparison with `memcmp()` compares bytes up to the specified number of
   bytes, independent of byte values.


# Part 5 - Input/Output

In this section, you will perform some hands-on exercises to better understand
file descriptors and reading and writing to files, including standard input,
standard output, and standard error.  Additionally, you will learn about
user-level buffering with file streams (`FILE *`).

 26. Read the man page for `stdin(3)` (which also shows the information for
     `stdout` and `stderr`).  Now use the `fileno()` and `printf()` functions
     to find and print out the file descriptor values for the `stdin`,
     `stdout`, and `stderr` file streams, each on its own line.  For example,
     the line corresponding to standard output would contain the string
     "stdout: n", where `n` is the descriptor value.

     *What are the file descriptor values for stdin, stdout, and stderr?*

 27. Use `memset()` to initialize every byte value in `buf` to `'z'` (or,
     equivalently, `0x7a`).  Then assign the byte at index 24 to `'\0'` (or,
     equivalently, 0).  Finally, call `memprint()` on `buf` to show the
     hexadecimal value of each byte/character (i.e., format `"%02x"`).

     *Does the output show any characters other than (ASCII) `z` and null?
     (Hint: It shouldn't.)*

 28. Print out the contents of `buf` to standard output in two ways:

     1. call `printf()` using the `"%s"` format string;
     2. call `write()`, specifying the integer file descriptor value for
        standard output; in this case, use `BUFSIZE` as the byte count.
        (Hint: see the
        [introduction section](#introduction---characters-encoding-and-presentation)).

     After each, print a newline character (`"\n"`), so each printout is on its
     own line.

     *Is there a difference between what was printed by `printf()` and what was
     printed by `write()`?  Why or why not?*  (Hint: See the `s` Conversion
     Specifier in the man page for `printf(3)`.)

 29. Print out the contents of `buf` to standard error (not standard out!) in
     two (new) ways:

     1. call `fprintf()`;
     2. call `write()`, specifying the integer file descriptor value for
        standard error; in this case, use `BUFSIZE` as the byte count.

     After each, print a newline character, so each printout is on its own
     line.

     Run the `./learn_c` command with "> /dev/null" appended to the end of the
     command line.

     *What happens to the output when you run with "> /dev/null" appended?*

 30. Run the `./learn_c` command with "2> /dev/null" appended to the end of the
     command line.

     *What happens to the output when you run with "2> /dev/null" appended?*

 31. Using the `open()` system call (not `fopen()`), open the file specified by
     the filename variable passing `O_RDONLY` as the only flag (i.e., open the
     file for reading only).  Save the return value as an integer variable,
     `fd1`.  Now copy that value to another integer variable, `fd2`.  Print out
     the values of `fd1` and `fd2`, each on its own line.

     *What is the significance of the value of `fd1`, i.e., the return value of
     `open()`?* (Hint: See the first two paragraphs of the DESCRIPTION for
     `open(2)`.)

 32. Use the `read()` system call to read up to 4 bytes from `fd1`, placing the
     bytes read into `buf`.  Save the return value as `nread`.  Add the value
     of `nread` to `totread`.  Then print the values of `nread` and `totread`,
     each on its own line (they should currently be the same).  Finally, call
     `memprint()` on `buf` using `BUFSIZE` showing each byte/character value as
     hexadecimal (i.e., format `"%02x"`).

     *Did the return value from `read()` match the count value passed in?  Why
     or why not?* (Hint: See the RETURN VALUE section in the man page for
     `read(2)`.)

 33. *Was a null character included in the bytes read or immediately following
     them?  Why or why not?*  (Hint: To answer the "why" question, use the
     `cat` and `hexdump` command-line utilities to inspect the contents of
     `test.txt`.)

 34. Use the `read()` system call to read up to 4 bytes from `fd2` (not
     `fd1`!).  Instead of using `buf` as the starting point at which the read
     data should be copied, use the offset into `buf` corresponding to the
     total bytes read (i.e., `buf + totread` or `&buf[totread]`). Save the
     return value as `nread`. Add the value of `nread` to `totread`.  Then
     print the values of `nread` and `totread`, each on its own line.
     Finally, call `memprint()` on `buf` using `BUFSIZE` showing each
     byte/character value as hexadecimal (i.e., format `"%02x"`).

     *Did this new call to `read()` start reading from beginning of the file or
     continue where it left off after the last call?  Why?* (Hint: See the
     RETURN VALUE section in the man page for `read(2)`.)

 35. You have now used two variables, in two different calls, to read from the
     file.  *Based on your answer to question 34, does the _address_ of the
     variable referencing a file descriptor matter, or only its _value_?*

 36. *How many total bytes have been read?*

 37. Repeat the instructions for question 34, but this time read up to
     `BUFSIZE - totread` bytes, instead of 4.

     *Did the return value from read() match the count value passed in?  Why or
     why not?* (Hint: See the RETURN VALUE section in the man page for
     `read(2)`.)

 38. *How many total bytes have been read?*

 39. *How many total bytes are in the file?* (Hint: Use the `stat` command-line
     utility to see the size of the file, in bytes.)

 40. *What would happen if `BUFSIZE` had been specified, instead of `BUFSIZE -
     totread` and there were still `BUFSIZE` bytes available to read?*

 41. Repeat the instructions for question 37.

     *What is the significance of the return value of `read()`?*
     (Hint: See the RETURN VALUE section in the man page for `read(2)`.)

 42. Use `printf()` to print the contents of `buf` to standard output using the
     `"%s\n"` format string.

     *How does the output compare to the actual contents of the file?  Briefly
     explain your response.* (Hint: See questions 28, 33, and 37.)

 43. Assign the value at index `totread` to the null character (`'\0'` or 0).
     Then repeat the instructions for question 42.

     *How does the output compare to the actual contents of the file?  Briefly
     explain your response.* (Hint: See questions 28, 33, and 37.)

 44. Call `close()` on `fd1`, and use `printf()` to print the return value on a
     line by itself.

     *What is the return value of `close()`?  What does this mean?* (Hint: See
     the RETURN VALUE section in the man page for `close(2)`.)

 45. Call `close()` on `fd2` (not `fd1`!) , and use `printf()` to print the
     return value on a line by itself.

     *What is the return value of this second instance of `close()`?  What does
     this mean, and what is the likely cause?* (Hint: See the RETURN VALUE
     section in the man page for `close(2)`. See also question 35.)

 46. Use `fprintf()` to print the following, in order:

     a. `"abc"` (no newline) to standard output

     b. `"def"` (no newline) to standard error

     c. `"ghi\n"` to standard output

     Then use `write()` to print the same three strings to the same locations,
     again.

     *What differences do you observe in the output of the strings using
     `fprintf()` vs. using `write()` and why?*  (Hint: See
     [intro](#printf-and-friends) and the "NOTES" section of the man page for
     `stdout(3)`.)

 47. Repeat the instructions from question 46.  However, this time, use the
     `fflush()` function to flush standard output immediately after printing
     `"abc"`.

     *What differences do you observe in the output of the strings using
     `fprintf()` vs. using `write()` and why?*


## Summary and Main Points

 - A file descriptor is allocated for every file-like object opened during a
   program execution.  This descriptor is simply an integer that is passed to
   functions like `write()`, `read()`, and `close()`.
 - Reading fewer bytes than requested means that all available bytes have been
   read.
 - When `read()` returns 0, it is a indicator that the file associated with the
   file descriptor has been closed (i.e., end-of-file).
 - File streams offer a higher-level interface for I/O, including buffering.


# Part 6 - Getting and Setting Environment Variables

In this section, you will write code that looks for the presence of an
environment variable and then practice getting and setting it.

 48. Use `getenv()` to assign the pointer `s1` to the string corresponding to
     the environment variable `CS324_VAR`.  If such a value exists, then print:
     `"CS324_VAR is _____\n"` (replace `_____` with the actual value);
     otherwise, print `"CS324_VAR not found\n"`.

     Run the following two commands:

     ```bash
     ./learn_c test.txt
     CS324_VAR=foo ./learn_c test.txt
     ```

     *What is the difference between running the commands?  Briefly explain.*

 49. Run the following two commands:

     ```bash
     export CS324_VAR=foo
     ./learn_c test.txt
     ```

     *How does this differ from running the first of the commands in question
     48?  Briefly explain.*


 50. (Upload your edited `learn_c.c` file to LearningSuite.)


## Summary and Main Points

 - Environment variables can be set on the command line (or with `setenv()`).
 - Environment variables can be retrieved by a C program using `getenv()`.
