import json
import crypt, getpass, pwd
#from passlib.hash import md5_crypt

 

K= 0
SEMAP = dict()
ESMAP = dict()
SALT = ''
IPT = ''



def readjson():
    with open('table.json') as data_file:
        data = json.load(data_file)
    tmpk = data["k"]
    tmpsalt = data["salt"]
    li = data["chains"]

    global K
    K = tmpk
    global SALT 
    SALT = tmpsalt
    print "K="+ str(K)
    print "SALT=" + str(SALT)

    l = len(li)
    for i in range(0, l):
        tmp = json.dumps(li[i])
        tmp2 = json.loads(tmp)
        key = tmp2["start"]
        value = tmp2["end"]
        SEMAP[key] = value
        ESMAP[value] = key


def calculatehelper(tmp):
    tmp = tmp[-8:]
    tmp = tmp[::-1]
    re = ''
    a = ord('a')
    for i in range(0, len(tmp)):
        r = (ord(tmp[i])%26) + a
        re = re + (chr(r))
    return re
        

def calculateR(code):
    flag = 0
    code = code.replace(SALT, '')
    print code
    
    global IPT
    IPT = code[-8:]
    print IPT

    re = code
    n = 0
    #print len(ESMAP)
    #print SEMAP["Wivestad"]
    while n <= K:
        m = calculatehelper(re)
        print m

        if m in ESMAP.keys():
            flag = flag + 1
            if flag > 1:
                result = ESMAP[m]
                print "Start Result: " + result
                return result
            else:
                continue
        else:
            #print "after R: " + m
            re = crypt.crypt(m, SALT)
            print re
            n = n + 1
            #print "getstart: "+ str(n)

    return ''
    
    
    #print start

def createChain(res, ipt):
    n = 0
    while(n<K):
        hres = crypt.crypt(res, SALT)
        if hres != ipt:
            rres = calculatehelper(hres)
            res = rres
            n = n + 1
            #print "getchain: " + str(n)
        else:
            print res
            break
    return res

    


readjson()
res = calculateR('$1$HUSKIES!$R9bstTQ9eG2Pzql0cq7kd/')
#print IPT
print res
print ESMAP.keys()
createChain(res, '$1$HUSKIES!$R9bstTQ9eG2Pzql0cq7kd/')

