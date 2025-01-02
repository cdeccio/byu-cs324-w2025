# Mirroring the Class GitHub Repository

Many of the assignments for this class are hosted in a GitHub repository.
Individual assignments are in subfolders of that repository.  Within the folder
for every assignment is a `README.md` file that contains the description for
the assignment.  The `README.md` is best viewed on the GitHub site itself using
a Web browser.  Alternatively, you can view the `README.md` from within VSCode,
by right-clicking the file and selecting the "Open Preview" option.  Every
assignment folder also contains other files that are part of the assignment.

To download and use the assignment folders and files, you will be creating a
and managing a _mirror_ of the class repository.  This will help ensure that
you have _all_ the files for the assignments, keep them up-to-date, and
simultaneously version your own code by committing it to your own private
GitHub repository.

The path of the upstream class repository and the name of your own private
repository have been given to you in the instructions to this assignment and
will be referred to in this document as "CLASS\_REPO\_PATH" and
"PRIVATE\_REPO\_NAME", respectively.  Additionally, "USERNAME" refers to your
GitHub username.  Thus, the following replacements should be made throughout
this document:

 - "CLASS\_REPO\_PATH": replace with the upstream class repository.
 - "PRIVATE\_REPO\_NAME": replace with the name of your own private repository.
 - "USERNAME": replace with your GitHub username.

These instructions have you first create your mirrored repository on your
primary development system and then optionally create clones of that repository
on other systems.


# Preparation

Your primary development system has been provided to you in the instructions
for this assignment.  Log on to your primary development system, either
directly or remotely via SSH.


# Register an SSH Key for Use with GitHub

These steps are necessary for you to use SSH to fetch and push your updates
from and to GitHub.  They should be performed on the primary development system
-- and later on any other systems on which you create clones.

If you already have an SSH key registered with GitHub on your system, then you
do not need to do this again.

 1. Find out if you already have an SSH key to use by running the `ls` command
    as follows:

    (The command is everything following the prompt `$` on the first line.)

    ```bash
    $ ls -ltra ~/.ssh/id_*
    -rw-r--r-- 1 user group  564 Jan  7 15:35 /home/user/.ssh/id_rsa.pub
    -rw------- 1 user group 2635 Jan  7 15:35 /home/user/.ssh/id_rsa
    ```

    In the above example, there is a public/private key pair named `id_rsa.pub`
    and `id_rsa`, respectively.  However, if there are no keys, `ls` will
    return an error:

    ```bash
    $ ls -ltra ~/.ssh/id_*
    ls: cannot access '/home/user/.ssh/id_*': No such file or directory
    ```

    If you have keys, then you can now go to step 3.  Otherwise, continue to
    step 2.

 2. Run the following from the command line to create an SSH public/private key
    pair:

    ```bash
    ssh-keygen
    ```

    At the following prompt, just hit enter to use the default file location:

    ```
    Enter file in which to save the key (/home/user/.ssh/id_rsa):
    ```

    Optionally enter a passphrase at the next prompt.  This makes sure that the
    private key cannot be used without the passphrase.  This is good practice
    for a shared machine in particular:

    ```
    Enter passphrase (empty for no passphrase):
    Enter same passphrase again:
    ```

 3. Display the contents of your _public_ key, and copy them to your clipboard.
    The following command prints the contents to the terminal:

    ```bash
    cat ~/.ssh/id_rsa.pub
    ```

    (This assumes the name of your public key file is `id_rsa.pub`, which is
    the default.)

 4. Follow steps 2 through 8 in the
    [official documentation](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account#adding-a-new-ssh-key-to-your-account)
    to register your SSH key with your GitHub account.


# Create a Mirrored Version of the Class Repository

This is a one-time process to create and configure your own private GitHub
repository for referencing and committing changes.  Your private repository
will also be a mirror of the upstream class repository.

 1. Create the private repository as a new repository on GitHub.  Follow steps 1
    through 6 in the
    [official documentation](https://docs.github.com/en/get-started/quickstart/create-a-repo#create-a-repository),
    adhering to the following:

    - Create the repository under your GitHub user ("USERNAME"), and name the
      repository according to PRIVATE\_REPO\_NAME (Step 2).
    - Make sure the visibility of the repository is _Private_ (Step 4).
    - Do _not_ check the box "Initialize this repository with a README" (Step 5).

 2. Please double-check that your repository is _private_.

 3. Clone the upstream class repository by running the following command in the
    terminal:

    (Substitute "CLASS\_REPO\_PATH" with the path of the upstream class
    repository.)

    ```bash
    git clone --bare https://github.com/CLASS_REPO_PATH upstream-repo
    ```

 4. Push a mirror of the upstream repository to the new, private repository,
    which you have just created:

    (Substitute "USERNAME" with your GitHub username and "PRIVATE\_REPO\_NAME"
    with the name of your private repository.)

    ```bash
    cd upstream-repo
    git push --mirror ssh://git@github.com/USERNAME/PRIVATE_REPO_NAME
    ```

 5. Remove your clone of the upstream repository.

    ```bash
    cd ../
    rm -rf upstream-repo
    ```


# Create a Clone of Your Private Repository

This is a one-time process to create a clone of the private repository you have
created.

 1. Clone your new, private repository, which is now a mirror of the upstream
    class repository:

    (Substitute "USERNAME" with your GitHub username and "PRIVATE\_REPO\_NAME"
    with the name of your private repository.)

    ```bash
    git clone ssh://git@github.com/USERNAME/PRIVATE_REPO_NAME
    ```

 2. Add the upstream repository to your clone:

    (Substitute "PRIVATE\_REPO\_NAME" with the name of your private repository
    and "CLASS\_REPO\_PATH" with the path of the upstream class repository.)

    ```bash
    cd PRIVATE_REPO_NAME
    git remote add upstream ssh://git@github.com/CLASS_REPO_PATH
    git remote -v
    ```

    Running `git remote -v` should produce four lines of output.  The two items
    that start with "origin" should point to your private repository, i.e.,
    "USERNAME/PRIVATE\_REPO\_NAME".  The two items that start with "upstream"
    should point to the class repository, i.e., "CLASS\_REPO\_PATH".  The
    presence of these entries means that your clone is associated primarily
    with your private repo ("origin"), and secondarily to the upstream class
    repository ("upstream").


# Create Additional Clones of Your Private Repository (Optional)

If you would like to create additional clones of your private repository on
other machines (e.g., a laptop), follow the instructions for both
[registering SSH keys](#register-an-ssh-key-for-use-with-github) and
[creating a clone](#create-a-clone-of-your-private-repository)
on _that_ machine.  Just remember that you will need to keep all clones
[up-to-date](#update-your-mirrored-repository-from-the-upstream)!


# Update Your Mirrored Repository from the Upstream

Throughout the semester we will be updating the class repository with changes
that seem appropriate.  Every time you start an assignment, and as often as you
like, please run the commands listed below to pull down the changes from the
upstream class repository and integrate them into your own private repository.
Remember that you will need to do this for any and all clones
[that you have made of your repository](#create-a-clone-of-your-private-repository).


 1. Pull down the latest changes from both your repository and the upstream:

    ```bash
    git fetch --all
    ```

 2. Stash (save aside) any uncommitted changes that you might have locally in
    your clone:

    ```bash
    git stash
    ```

 3. Merge in the changes from the upstream repository:

    ```bash
    git merge upstream/master
    ```

 4. Merge back in any uncommitted changes that were stashed:

    ```bash
    git stash pop
    ```

 5. Push out the locally merged changes to your repository:

    ```bash
    git push
    ```


# Commit and Push Local Changes to Your Private Repo

It is best practice to regularly commit your changes and push them to the
origin.  Follow the steps below every time you want to commit changes to the
clone of your repository and push them out to your private repository on
GitHub:

 1. Mark modified files as "staged" for the next commit.

    (Replace "..." with the names of any files or directories that have
    changes.)

    ```bash
    git add ...
    ```

 2. Commit files staged for commit.

    ```bash
    git commit
    ```

    Note that will open an editor within which you can enter a message
    associated with your commit.  Alternatively you can use the `-m`
    command-line option to add your message directly from the command line,
    without using an enter.  For example: `git commit -m "improve my code"`.

 3. Push your local commits to your private repository on GitHub:

    ```bash
    git push
    ```

NOTE: The add and commit process above isn't the only way to commit your local changes.
The offical git documentation for [`git commit`](https://git-scm.com/docs/git-commit) lists
several other ways you can commit your local changes.
