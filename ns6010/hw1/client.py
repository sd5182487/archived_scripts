#! /usr/bin/python2

import sys
import socket
import struct
import json
import base64

from Crypto.Cipher import ARC4

def main():
    '''
    Main.
    '''

    if len(sys.argv) < 3:
        print 'usage: {} <host> <port>'.format(sys.argv[0])
        return 1

    host = sys.argv[1]
    port = int(sys.argv[2])

    sk = socket.socket()
    sk.connect((host, port))

    key = '\xeb\xb0\x18\xbd\xa2\x09\xde\xbb\xc4\x5e\x77\x00\xdc\x0e\x99\xb5'

    l = struct.unpack('>I', sk.recv(4))[0]
    buf = sk.recv(l)
    enc = ARC4.new(key)
    msg = json.loads(enc.encrypt(buf))
    print msg

    s = base64.b64decode(msg('secret'))[0]
    msg['secret'] = base64.b64encode(s)
    enc.encrypt(json.dumps(msg))

    sk.sendall(struct.pack('>I', len(buf)))
    sk.snedall(buf)

    l = struct.unpack('>I', sk.recv(4))[0]
    buf = sk.recv(l)
    msg = json.loads(enc.encrypt(buf))
    print msg

    sk.close()

    return 0

if __name__ == '__main__':
    sys.exit(main())
