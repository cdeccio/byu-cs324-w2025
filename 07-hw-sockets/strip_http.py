#!/usr/bin/env python3

import sys

def main():
    data = sys.stdin.buffer.read()
    i = 0
    while i < len(data):
        if data[i:i+4] == b'\r\n\r\n':
            break
        i += 1
    if i != len(data):
        data = data[i+4:]
    sys.stdout.buffer.write(data)

if __name__ == '__main__':
    main()
