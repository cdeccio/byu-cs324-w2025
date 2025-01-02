#!/usr/bin/python3

# slow-client.py - This is a client that makes an HTTP request very slowly, so
#                  it forces the proxy to read the request across multiple reads.
#
# usage: slow-client.py <proxy_url> <origin_url> <sleeptime> <timeout> <output>
#
import argparse
import signal
import socket
import sys
import time
import urllib.parse

def handle_alarm(sig, frame):
    sys.exit(28)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--max-time', type=int, action='store', default=60)
    parser.add_argument('-o', '--output', type=argparse.FileType('wb'), action='store', default=sys.stdout.buffer)
    parser.add_argument('-x', '--proxy', type=urllib.parse.urlparse, action='store')
    parser.add_argument('-b', '--sleep-between-send', type=int, action='store', default=0)
    parser.add_argument('url', type=urllib.parse.urlparse, action='store')
    args = parser.parse_args(sys.argv[1:])

    signal.signal(signal.SIGALRM, handle_alarm)

    if args.proxy:
        (scheme, netloc, path, params, query, fragment) = args.proxy
        try:
            host, port = netloc.split(':')
        except ValueError:
            host = netloc
            port = 8080
        else:
            port = int(port)
        (scheme, netloc, path, params, query, fragment) = args.url
        uri = urllib.parse.urlunparse(args.url)
    else:
        (scheme, netloc, path, params, query, fragment) = args.url
        try:
            host, port = netloc.split(':')
        except ValueError:
            host = netloc
            port = 80
        else:
            port = int(port)
        if not path:
            path = '/'
        if query:
            uri = '%s?%s' % (path, query)
        else:
            uri = path

    # set an alarm, so we can exit if it times out
    signal.alarm(args.max_time)

    addrs = socket.getaddrinfo(host, port, socket.AF_UNSPEC,
                              socket.SOCK_STREAM, 0)
    connected = False
    exc = None
    for (family, socktype, proto, canonname, sockaddr) in addrs:
        s = socket.socket(family, socktype)
        try:
            s.connect(sockaddr)
        except socket.error as e:
            exc = e
        else:
            connected = True

    if not connected:
        raise exc

    time.sleep(args.sleep_between_send)
    s.send(bytes('GET %s HTTP/1.0\r\n' % (uri), 'utf-8'))
    time.sleep(args.sleep_between_send)
    s.send(bytes('Host: %s\r\n\r\n' % (netloc), 'utf-8'))

    content = b''
    while True:
        buf = s.recv(1024)
        if not buf:
            break
        content += buf

    # remove handler
    signal.signal(signal.SIGALRM, signal.SIG_IGN)

    start_of_headers = content.find(bytes('\r\n\r\n', 'utf-8'))

    if start_of_headers >= 0:
        args.output.write(content[start_of_headers+4:])
    args.output.flush()

if __name__ == '__main__':
    main()
