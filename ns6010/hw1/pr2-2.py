import json
import crypt, getpass, pwd
 

K= 0
SEMAP = dict()
ESMAP = dict()
SALT = ''
IPT = ''

def readjson(filepath):
   	with open(filepath) as data_file:
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
	re = ''
	a = ord('a')
	for i in range(0, len(tmp)):
		r= (ord(tmp[i])%26) + a
		re = re + (chr(r))
	return re
		

def calculate(code):
	code = code.replace(SALT,'')
	
	global IPT
	IPT = code[-8:]
	re = code

	n = 0
	while(n<=K):
		m = calculateR(re)
		n = n+1
		if m in ESMAP.keys():
			result = ESMAP[m]
			print "Start Result: "+result
			break
		else:
			
			re = crypt.crypt(m, SALT)	
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
		else:
			print 'Final result: '+result
			break
	return result

	

    


path = raw_input('Enter table file path:')
readjson(path)

code = raw_input('Enter the code:')
print 'Calculating start value...'
res = calculate(code)
print 'Calculating final value...'
createChain(res, code)

   


   
