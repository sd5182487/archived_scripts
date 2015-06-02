import json
import crypt

SALT = ''
K = ''

def crack(hash_value, chain_table):
    tmp = hash_value
    for i in range(K):
        end = reduce(hash_value)
        if end in chain_table.keys():
            start = chain_table[end]
            password = deduce(start, tmp)
            if password is not None:
                return password
        hash_value = md5_hash(end)
    return None

def deduce(start, hash):
    s = start
    for i in range(K):
        h = md5_hash(s)
        if h == hash:
            return s
        s = reduce(h)
    return None

def md5_hash(key):
    return crypt.crypt(key.encode('utf8'), SALT)

def reduce(value):
    s = value[-8:]
    s = s[::-1]
    ret = ''
    for c in s:
        ret += chr(ord(c) % 26 + ord('a'))
    return ret

def eff(table, k):
    key_set = set()
    for e, s in table.iteritems():
        print "Walk " + s + ", " + e
        key_set.add(s)
        end = s
        while end != e:
            h = md5_hash(end)
            end = reduce(h)
            key_set.add(end)
    return len(key_set)/float(k * len(table))

table_path = "table.json"
input_data = {"aoun": "$1$HUSKIES!$v/mh7SBLm8/3SBL6w0Z9M1",
              "curry": "$1$HUSKIES!$xk2VnxpJYAGOxEl0W8uEP0",
              "ryder": "$1$HUSKIES!$R9bstTQ9eG2Pzql0cq7kd/"}

with open(table_path, 'r') as f:
    content = json.load(f)

SALT = content["salt"]
K = content["k"]
chains = content["chains"]
table = {}
result = {}
for pair in chains:
    table[pair["end"]] = pair["start"]

print "Crack pass"
for u, h in input_data.iteritems():
    result[u] = crack(h, table)
print result

print "Calculate Efficiency: "
print eff(table, K)
