import json
import crypt, getpass, pwd
 

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


def calculateR(tmp):
    tmp = tmp[-8:]
    tmp = tmp[::-1]
    #print tmp
    re = ''
    a = ord('a')
    for i in range(0, len(tmp)):
        r= (ord(tmp[i])%26) + a
        re = re + (chr(r))
    return re
        

def calculate(code):
    code = code.replace(SALT, '')
    print code
    
    global IPT
    IPT = code[-8:]
    print IPT
    print len(ESMAP)
    re = code
    n = 0

    while(n<=K):
        m = calculateR(re)
        print m
        if m in ESMAP.keys():
            print m
            result = ESMAP[m]
            print n
            print "Start Result: "+result
            break
        else:
            #print "after R: " + m
            re = crypt.crypt(m, SALT)
            print re            
            n = n+1
            #print "getstart: "+ str(n)
    return result
    
    
    #print start

def createChain(res,ipt):
    n = 0
    while(n<K):
        result = res
        hres = crypt.crypt(res,SALT)    
        if hres != ipt:
            rres = calculateR(hres)
            res = rres
            n = n + 1
            #print "getchain: " + str(n)
        else:
            print result
            print hres
            break
    return result

    

    


readjson()
res = calculate('$1$HUSKIES!$v/mh7SBLm8/3SBL6w0Z9M1')
print IPT
createChain(res, '$1$HUSKIES!$v/mh7SBLm8/3SBL6w0Z9M1')

   

