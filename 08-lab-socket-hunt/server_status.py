#!/usr/bin/env python3

import hashlib
import os
import socket
import sys
import threading

PORT = 32400

SERVERS = [ 'arizona', 'alaska', 'carolina', 'california', 'idaho', 'hawaii',
           'michigan', 'indiana', 'rhodeisland', 'oregon', 'tennessee',
           'wyoming' ]

lock = threading.Lock()
status = {}

def check_server(server):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(2)
    try:
        s.connect((server, PORT))
        s.send(b'')
        s.recv(1)
        stat = True
    except OSError:
        stat = False

    with lock:
        status[server] = stat

def user_specific_index(total):
    if total < 1:
        return None
    uid = os.geteuid()
    digest = hashlib.sha1(uid.to_bytes(4, byteorder='big')).hexdigest()
    hashed_int = int(digest[-8:], 16)
    return hashed_int % total

def get_status():
    threads = []
    for server in SERVERS:
        status[server] = None
    for server in SERVERS:
        t = threading.Thread(target=check_server, args=(server,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

def show_full_status():
    sys.stdout.write('Overall server status:\n')
    i = 0
    for server in SERVERS:
        if status[server]:
            stat = '\033[32mOK\033[0m'
        else:
            stat = '\033[31mDOWN\033[0m'
        sys.stdout.write('%15s: %13s  ' % (server, stat))
        i += 1
        if i % 3 == 0:
            sys.stdout.write('\n')

def show_preferred_server():
    up_servers = [s for s in SERVERS if status[s]]
    index = user_specific_index(len(up_servers))
    if index is None:
        sys.stdout.write('All servers are down!\n')
    else:
        sys.stdout.write('Preferred server (for your user): %s\n' % \
                up_servers[index])

def main():
    get_status()
    show_full_status()
    show_preferred_server()

if __name__ == '__main__':
    main()
