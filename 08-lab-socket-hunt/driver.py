#!/usr/bin/python3

import argparse
import hashlib
import random
import re
import socket
import subprocess
import struct
import sys
import threading
import time

NUM_LEVELS = 5
SEEDS = [7719, 33833, 20468, 19789, 59455]
CLIENT = './treasure_hunter'
BYTES_MINUS_CHUNK = 8
TIMEOUT = 20

LEVEL_SCORES = { 0: 50, 1: 15, 2: 15, 3: 15, 4: 5 }
LEVELS_EXTRA_CREDIT = [ 4 ]

SUMS = ['3e7949f4943f1d40959c87166a46e0433665fb19',
        '4175db5d21868441178f14ed431eb0a6b587a9cf',
        '6e49aceeb8a870a9a131064862442f3b0664a31f',
        '254da7877caff8c91cff192b02ef4dec658e8401',
        '39a6b49799b21986e60e6777a5650a377a03890c',
        '72a0e348530a522b172497fbab4dccddd609fb18',
        'd10f59f215cdf4b3e4cbe338f3b470dd0f1ae206',
        'ef454bccd3384c0df7a7e9296763857379b3381b',
        '461e8be6540b5d11c19b89afbe18c4bfd6b9ff24',
        '6073c4db64a9d94e831a4449030461819ce875ca',
        '715ec633372a4296cf33a168dafdefe7fd9acd16',
        '528725f471a7cf184b482bac0e6339edc89daa36',
        '327d51bb647a904ad38bbb1cc3089a9135ffaf7d',
        '0796bf7759f707ef55218bd9ccf405ef8f6fc882',
        'd8e1d8f75a408e3ad40156f94a5d779c4626ff9c',
        '30242ce853936406789d806c1fb6b95a535bc013']

RECV_RE = re.compile('^recv(from)?.* = (\d+)$')

level_seed_result = (False, 0, None, None)

def tmp_server(port):
    global level_seed_result
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(1)
    s.bind(('127.0.0.1', port))

    try:
        (buf, addr) = s.recvfrom(65536)
    except socket.timeout:
        return
    if len(buf) != 8:
        level_seed_result = (True, len(buf), None, None)
        return
    level, userid, seed = struct.unpack('!HIH', buf[:8])
    level_seed_result = (True, len(buf), level, seed)

def test_level_seed(level, seed):
    global level_seed_result
    port = random.randint(1024, 65535)
    level_seed_result = (None, None)
    t = threading.Thread(target=tmp_server, args=(port,))
    t.start()
    cmd = [CLIENT, '127.0.0.1', str(port), str(level), str(seed)]
    p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)
    t.join()
    p.kill()
    if not level_seed_result[0]:
        return f'Client does not communicate with port provided on command line ({port})'
    if level_seed_result[1] != 8:
        return f'Initial message length invalid ({level_seed_result[1]}).'
    if level_seed_result[2] != level:
        return f'Level sent by client ({level_seed_result[2]}) is different from that provided on command line ({level}).'
    if level_seed_result[3] != seed:
        return f'Seed sent by client ({level_seed_result[3]}) is different from that provided on command line ({seed}).'
    return ''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('server', action='store', type=str)
    parser.add_argument('port', action='store', type=int)
    parser.add_argument('level', action='store', type=int,
        nargs='?', choices=range(NUM_LEVELS))
    args = parser.parse_args(sys.argv[1:])

    if args.level is None:
        levels = range(NUM_LEVELS)
    else:
        levels = [args.level]

    score = 0
    max_score = 0
    for level in levels:
        if level in LEVELS_EXTRA_CREDIT:
            extra_credit_str = ' (extra credit)'
        else:
            extra_credit_str = ''
        sys.stdout.write(f'Testing level {level}{extra_credit_str}:\n')
        for seed in SEEDS:
            if level not in LEVELS_EXTRA_CREDIT:
                max_score += LEVEL_SCORES[level] / len(SEEDS)
            sys.stdout.write(f'    Seed %5d:' % (seed))
            sys.stdout.flush()

            warn_msg = test_level_seed(level, seed)

            cmd = ['strace', '-e', 'trace=%network',
                    CLIENT, args.server, str(args.port), str(level), str(seed)]
            try:
                p = subprocess.run(cmd,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        timeout=TIMEOUT)
            except subprocess.TimeoutExpired:
                treasure = b''
                treasure_len = 0
                strace_output = b''
                h = ''
            else:
                treasure = p.stdout
                if treasure and treasure.endswith(b'\n'):
                    treasure = treasure[:-1]
                treasure_len = len(treasure)
                strace_output = p.stderr
                h = hashlib.sha1(treasure).hexdigest()

            tot_bytes = 0
            output = strace_output.decode('utf-8').strip()
            for line in output.splitlines():
                # skip DNS lookups
                if 'htons(53)' in line:
                    continue
                m = RECV_RE.search(line)
                if m is not None:
                    received_bytes = int(m.group(2))
                    if received_bytes > 1:
                        tot_bytes += received_bytes - BYTES_MINUS_CHUNK
            
            if h not in SUMS:
                sys.stdout.write(f' FAILED: output does not match')
            elif tot_bytes != treasure_len:
                sys.stdout.write(f' FAILED: invalid number of bytes received')
            else:
                score += LEVEL_SCORES[level] / len(SEEDS)
                sys.stdout.write(f' PASSED')
            if warn_msg:
                sys.stdout.write(f' (warning: {warn_msg})')
            sys.stdout.write('\n')
            
    print(f'Score: {score}/{max_score}')
            
if __name__ == '__main__':
    main()
