# Install Linux on a VM

The point of this exercise is to install a Linux-based OS on a Virtual Machine
(VM) for development in this class.

Notes:
 - While you can develop, compile, and test on this VM, you must eventually
   compile and test your code on the BYU CS lab machines before submitting it.
   They are quite possibly a different kernel and architecture!
 - If using UTM/Qemu on MacOS (Apple M1 or M2 chip) solution, some of the
   binaries provided will not run on your VM system, as they were compiled to
   be run on the BYU CS lab machines.


 - [VirtualBox 7.x for Windows, Linux, and MacOS (amd64 only)](#virtualbox-7x-for-windows-linux-and-macos-amd64-only)
 - [UTM/Qemu on MacOS (required for Apple Silicon (M1/M2/M3))](#utmqemu-on-macos-required-for-apple-silicon-m1m2m3)

# VirtualBox 7.x for Windows, Linux, and MacOS (amd64 only)

Please note that for Mac systems using Apple Silicon (M1/M2/M3), you should use the
UTM/Qemu instructions.

These instructions are for VirtualBox 7.x.  For versions other than 7.x, you
might need to adapt these instructions.

 1. Download and install
    [VirtualBox](https://www.virtualbox.org/wiki/Downloads).

 2. Download the "netinst" (net install) image with amd64 architecture from
    [Debian](https://www.debian.org/releases/stable/debian-installer/).

 3. Start VirtualBox, and click "New" to create a new VM.

 4. At the "Virtual machine Name and Operating System" dialog, enter the
    following:

    a. Name: Give the VM a meaningful name (e.g., "cs460").

    b. Folder: Use the default folder value.

    c. ISO Image: Select the install image (`.iso` file) you downloaded in
       step 2.

    d. Check the box labeled "Skip Unattended Installation".

    Click "Next".

 5. At the "Hardware" dialog, enter the following:

    a. Base Memory: Give the machine 2GB (2048 MB) of RAM.

    b. Processors: Select 2 if you think your machine has at least four cores;
       select 1 otherwise.

    c. Enable EFI: Leave this default

    Click "Next".

 6. At the "Virtual Hard Disk" dialog, enter the following:

    a. "Create a virtual Hard Disk Now": 20 GB

    b. "Preallocate Full Size" - leave unchecked

    Click "Next".

 7. At the "Summary" dialog, click "Finish".

 8. In the VM, go through the Debian installation using all the default options,
    except for the following:

    a. At the "Partition Disks" dialog, you will be asked if you want to write
       changes to disk.  You will need to change the answer from the default
       ("No") to "Yes".

    b. At the "Software selection" dialog, make sure the following boxes are
       checked:

       - "Debian desktop environment"
       - "LXDE"
       - "Standard System Utilities"

       Uncheck any other other options ("GNOME", "SSH server", etc.).  This is
       intended to be a lightweight system that provides the essentials for this
       class.  LXDE provides a lightweight desktop environment that demands less
       of your host system.

    c. If the "GRUB boot loader" dialog appears, select your hard disk to allow
       the installer to install GRUB to the hard drive.  It should start with
       "/dev" (probably "/dev/sda").

    Your VM should reboot when installation has finished.

 9. Log in to the VM after it reboots.  Use the regular account (i.e., non-root)
    username and password that you created during installation.

 10. Within the LXDE desktop environment in the VM, open a terminal
     (`LXTerminal`) and do the following to add yourself to the `sudo` group:

     a. Run the following from the command line to temporarily become `root`
        (system administrator):

        ```
        $ su -
        ```

        When prompted, enter the password for the `root` user.

     b. At the `root` (`#`) prompt, run the following to add your user to the
        `sudo`:

        ```
        # usermod -a -G sudo $USER
        ```

        (Replace `$USER` with the username of your regular, non-root user.

        Note, however, that when running later commands with `sudo`, you will be
        able to leave `$USER` as-is because the shell will automatically
        replace it with your username before the command is run.  However, in
        this case, the user running the command is `root`, so `$USER`, would be
        replaced with `root`, not your username, and that is not what you want.)

 11. In the VM, log out of LXDE and log back in.  As a member of the `sudo`
     group, you will be able to run commands that require administrator
     privileges on a command-by-command basis using `sudo`, rather than working
     as the `root` user, which is discouraged.

 12. Do the following to to install the VirtualBox Guest additions:

     a. On the host system, select "Devices" from the VirtualBox menu, then select
        "Insert Guest Additions CD Image...".

     b. Within the LXDE desktop environment in the VM, open a terminal
        (`LXTerminal`).

     c. From the open terminal, run the following to mount the "inserted"
        virtual CD containing the guest additions.

        ```
        $ mount /media/cdrom
        ```

     d. From the open terminal, run the following commands to build and install
        the VirtualBox Guest Additions for your VM:

        ```
        $ sudo apt install linux-headers-amd64 build-essential
        $ sudo sh /media/cdrom/VBoxLinuxAdditions.run
        ```

     e. Reboot your VM to have the changes take effect.

     f. Log in to the VM after it reboots.  Use the regular account (i.e.,
        non-root) username and password that you created during installation.

    This will allow you to do things like set up a shared drive between host
    and VM and use a shared clipboard, which will be accomplished in a
    subsequent step.

 13. On the host machine, do the following to set up a shared folder:

     a. From VirtualBox "Devices" menu, select "Shared Folders" then "Shared
        Folders Settings...".

     b. Click the button to add a shared folder.

     c. Choose which folder from the _host_ system you would like to share
        (e.g., `/Users/$HOSTUSER/shared`, where your actual username on the
        host OS replaces `$HOSTUSER`).

     d. Choose the location where the shared folder from the host will be
        mounted within the OS on the VM (e.g., `/home/$GUESTUSER/shared`,
        where your actual username on the VM replaces `$GUESTUSER`).

     e. Select both "Auto-mount" and "Make permanent".

     For more information, see the
     [official documentation](https://www.virtualbox.org/manual/ch04.html#sharedfolders).

14. Within the VM, do the following from a prompt to add your user to the
    `vboxsf` (VirtualBox shared folders) group:

    ```
    $ sudo usermod -a -G vboxsf $USER
    ```

15. In the VM, log out of LXDE and log back in.  As a member of the `vboxsf`
    group, you will be able to access the folder `/Users/$HOSTUSER/shared` (or
    whichever folder you selected) on the host from `/home/$GUESTUSER/shared`
    (or whichever mount point you selected) in the VM.

16. On the host machine, do the following to enable copy and paste between
    your host and your VM.

    From the VirtualBox "Devices" menu, select "Shared Clipboard" then
    "Bidirectional".

17. In the VM, open a terminal, and run the following to remove some unnecessary
    packages from your VM:

    ```
    $ sudo apt purge libreoffice-{impress,math,writer,draw,base-core,core,help-common,core-nogui} xscreensaver
    $ sudo apt autoremove
    ```

 18. In the VM, disable the screen locker by doing the following:

     a. Select "Preferences" then "Desktop Session Settings" from the menu.

     b. Uncheck the box titled "Screen Locker," and click "OK".

     c. Log out of LXDE and log back in.

 19. In the VM, open a terminal, and run the following to install a few packages
     that will be useful for you in this class:

     ```
     sudo apt install git tmux vim build-essential make
     ```

 20. Install whatever other tools and utilities that you think will improve your
     development environment.  Please note that if you have configured shared folders
     as described above, you can use whatever development environment you have already
     installed on your host to manipulate files in `/home/$USER/shared` or some
     subfolder thereof.  Thus, you do not have to develop within the VM itself if you
     do not want to.


# UTM/Qemu on MacOS (required for Apple Silicon (M1/M2/M3))

 1. Install [Homebrew](https://brew.sh/).

 2. Install qemu and utm:

    ```bash
    brew install utm qemu
    ```

 3. Download the "netinst" (net install) image from
    [Debian](https://www.debian.org/releases/stable/debian-installer/).
    For M1/M2/M3 hardware, use the arm64 architecture.  For anything else, use
    amd64.
 3. Download the "netinst" (net install) image from
    [Debian](https://www.debian.org/releases/stable/debian-installer/).
    For M1/M2 hardware, use the arm64 architecture.  For anything else, use
    amd64.

 4. Start UTM, then do the following:

    a. Click the "+" button to create a new virtual machine.

    b. Start: Click "Virtualize"

    c. Operating System: Click "Linux".

    d. Linux: Under "Boot ISO Image", click "Browse", then select the install
       image (`.iso` file) you downloaded.  Then click "Continue".

    e. Hardware: Specify at least 2048 MB RAM, then click "Continue".

    f. Storage: Specify at least 20GB, then click "Continue".

    g. Shared Directory: Select a folder from the _host_ system that you would
       like to share (e.g., `/Users/$HOSTUSER/shared`, where your actual
       username on the host OS replaces `$HOSTUSER`).  Then click "Continue".

    h. Click "Play".

 5. Follow steps 8 through 11 from the
    [VirtualBox instructions](#virtualbox-7x-for-windows-linux-and-macos-amd64-only).

    Before the system reboots (the final installation step), "remove" the
    install CD by doing the following within the host system:

    a. Click the "Drive Image Options" button.

    b. Select "CD/DVD (ISO) Image".

    c. Click "Eject".

 6. Within the guest OS, open a terminal, and run the following from the command
    to install utilities for allowing the host to interact with the guest:

    ```bash
    sudo apt install spice-vdagent
    ```

 7. Reboot your VM to have the changes take effect.

 8. Mount the shared directory.

    a. Create a mount point on the VM:

       ```bash
       sudo mkdir /media/shared
       ```

    b. Mount the shared volume as type `9p`:

       ```bash
       sudo mount -t 9p -o trans=virtio,version=9p2000.L share /media/shared/
       ```

    c. Change the permissions (from only the VM perspective) on files and
       directories in the shared directory, so your user (in the VM) can access
       the files.

       ```bash
       sudo chown -R $USER /media/shared/
       ```

      (Note: You can leave `$USER` as-is because the shell will automatically
      replace it with your username before the command is run.  You can see
      this by running `echo $USER`.)

    d. Test your new mount by listing directory contents:

       ```bash
       ls -l /media/shared
       ```

    e. Add the following line to `/etc/fstab` such that the shared volume is
       mounted automatically at boot:

       ```
       share	/media/shared	9p	trans=virtio,version=9p2000.L,rw,_netdev,nofail	0	0
       ```

    f. Optionally create a symbolic link to the share mount from your home
       directory:

       ```bash
       ln -s /media/shared/ ~/shared
       ls -l ~/shared
       ```


10. Follow steps 17 through 20 from the
   [VirtualBox instructions](#virtualbox-7x-for-windows-linux-and-macos-amd64-only).
