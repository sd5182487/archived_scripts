# Implementation of needham-schroeder process
# A -> S : A, B, Na
# S -> A : {Na, Kab, B, {Kab, A}Kbs}Kas
# A -> B : {Kab, A}Kbs
# B -> A : {Nb}Kab
# A -> B : {Nb-1}Kab

import socket
import json
import struct
import base64
from Crypto.Cipher import ARC4

HOST = "127.0.0.1"
PORT_S = 5452
PORT_B = 5453
Kas = '\xeb\xb0\x18\xbd\xa2\x09\xde\xbb\xc4\x5e\x77\x00\xdc\x0e\x99\xb5'

print "Step 1: A -> S : A, B, Na"
ini_msg = dict()
ini_msg["client_id"] = "cheerfulinteger"
ini_msg["server_id"] = "secret"
ini_msg["nonce"] = 11
sk_s = socket.socket()
sk_s.connect((HOST, PORT_S))
msg = json.dumps(ini_msg)
sk_s.sendall(struct.pack('>I', len(msg)))
sk_s.sendall(msg)
l = struct.unpack('>I', sk_s.recv(4))[0]
buf = sk_s.recv(l)
enc_as = ARC4.new(Kas)
msg = json.loads(enc_as.encrypt(buf))
print "Receive {Na, Kab, B, {Kab, A}Kbs}"
print msg
sk_s.close()


print "Step 2: A -> B : {Kab, A}Kbs"
Kab = base64.b64decode(msg["session_key"])
blob = msg['blob']
msg = base64.b64decode(blob)
sk_b = socket.socket()
sk_b.connect((HOST, PORT_B))
sk_b.sendall(struct.pack('>I', len(msg)))
sk_b.sendall(msg)
l = struct.unpack('>I', sk_b.recv(4))[0]
buf = sk_b.recv(l)
enc_ab = ARC4.new(Kab)
msg = json.loads(enc_ab.encrypt(buf))
nonce = msg["nonce"]
print "Receive {Nb}"
print nonce

print "Step 3: A -> B : {Nb-1}Kab"
msg = dict()
msg["nonce"] = nonce-1
msg = enc_ab.encrypt(json.dumps(msg))
sk_b.sendall(struct.pack('>I', len(msg)))
sk_b.sendall(msg)
l = struct.unpack('>I', sk_b.recv(4))[0]
buf = sk_b.recv(l)
msg = json.loads(enc_ab.encrypt(buf))
sec = msg["secret"]
print "Receive secret"
print sec
sk_b.close()