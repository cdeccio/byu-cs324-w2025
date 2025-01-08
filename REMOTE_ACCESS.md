# Remote Access to CS Lab Machines

Throughout this class, you will be required to access to the CS lab machines to
complete various assignments.  You are welcome to log on to a CS lab machine
directly, by sitting at a workstation in one of the labs.  However, you can
also access them remotely, which is often more convenient.

 1. Get on to the CS network.

    To access the CS lab machines, you must first be inside the CS network.
    There are two ways to do this:

    - *If you are in the TMCB*, simply connect to the "eduroam" WiFi.  If you
      are in the TMCB and you are currently enrolled in a CS class, then
      connecting to "eduroam" gives you access to the CS lab machines.

    - *If you are outside the TMCB, including off-campus and other parts of
      campus*, [install the BYU CS VPN](https://cs-vpn.byu.edu/), if you
      haven't already.  Then connect to the BYU CS VPN by opening the software
      you installed and connecting to the VPN at "cs-vpn.byu.edu".

 2. Access a the CS Lab Machines.

    At this point, you can access an arbitrary CS lab machine remotely over SSH
    by running the following from a terminal on your machine:

    ```bash
    ssh yournetid@schizo.cs.byu.edu
    ```

    You can think of schizo as a load balancer for SSH.  Note that your home
    directory is shared across all lab machines (using the network file server
    or NFS), so you can access the files in your home directory no matter which
    lab machine you log in to.

    Alternatively, you can access *individual* CS machines remotely over SSH by
    running the following:

    (Replace "hostname" with the name of the machine to which you are logging on.
    For example: "florida", "idaho", or "alabama")

    ```bash
    ssh yournetid@hostname.cs.byu.edu
    ```

    In addition to remote terminal access with the `ssh` command, you can also
    use `scp` (for copying files securely) and VS Code with the SSH Remote
    extension.
