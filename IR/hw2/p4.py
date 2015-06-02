#!/usr/bin/python
__author__ = 'haohuang'
# This is a simple word frequent/association calculator script
# for CS6200 IR
# written in 7/2014
# thanks Yilin for much helps
from operator import itemgetter
from math import log10


unique_word = 0
unique_bigram = 0
dic = []
top_ten = []
count = {}
bcount = {}

f = open('output.txt')
result = f.readlines()
f.close()
total_words = len(result)
for word in result:
    word = word.rstrip('\n')
    if word in count:
        count[word] += 1
    else:
        unique_word += 1
        count[word] = 1

lsorted = sorted(count.items(), key=itemgetter(1), reverse=True)

f = open('b_output.txt')
result = f.readlines()
f.close()
total_bigrams = len(result)
for bigram in result:
    bigram = bigram.rstrip('\n')
    if bigram in bcount:
        bcount[bigram] += 1
    else:
        unique_bigram += 1
        bcount[bigram] = 1


def swap_bigrams(bcount):
    processed_bigram = []
    for bigram in bcount:
        if bigram not in processed_bigram:
            processed_bigram.append(bigram)
            dic = bcount[bigram]
            line = bigram.split(' ')
            shift_bigram = line[1] + ' ' +line[0]
            if shift_bigram in bcount:
                processed_bigram.append(shift_bigram)
                dic += bcount[shift_bigram]
                bcount[bigram] = dic
                bcount[shift_bigram] = dic

bsorted = sorted(bcount.items(), key=itemgetter(1), reverse=True)

######## 1.
######## bigram frequency
rank = 0
index = 0

for (value, times) in bsorted:
    rank += 1
    prob = float(times)/total_bigrams
    current = (value, prob)
    dic.append(current)

with open("bigram_freq.txt", "w") as o:
    o.write('%-20s %-10s\n' % ("word", "frequency"))
    for (value, prob) in dic:
        o.write('%-20s %-10s\n' % (value, prob))



#find top 10 words in p1
swap_bigrams(bcount)

p = open("p1.txt", "r")
output = p.readlines()
p.close()
for word in output:
    word = word.rstrip('\n')
    if index < 11:
        top_ten.append(word.split(' ')[0])
        index += 1
top_ten = top_ten[1:]


def algo_MIM(bigram):
    line = str(bigram).split(' ')
    a = count[line[0]]
    b = count[line[1]]
    ab = float(bcount[bigram])
    return ab / (a * b)


def algo_EMIM(bigram):
    return float(bcount[bigram]) * log10(total_words * algo_MIM(bigram))


def algo_chisqr(bigram):
    line = str(bigram).split(' ')
    a = count[line[0]]
    b = count[line[1]]
    ab = float(bcount[bigram])
    return ((ab - (float(a * b) / total_words)) ** 2) / (a * b)

def algo_Dice(bigram):
    line = str(bigram).split(' ')
    a = count[line[0]]
    b = count[line[1]]
    ab = float(bcount[bigram])
    return ab / (a + b)

with open('top_ten_bigram.txt', 'w') as t:
    t.write("Top ten words:" + str(top_ten) + '\n')
    for word in top_ten:
        for bigram, value in bsorted:
            line = str(bigram).split(' ')
            if word == line[0] or word == line[1]:
                t.write("Association Measure for word -- " + str(word) + " -- bigram:" + str(bigram) + '\n')
                t.write("MIM:" + str(algo_MIM(bigram)) + '\n')
                t.write("EMIM:" + str(algo_EMIM(bigram)) + '\n')
                t.write("CHISQ:" + str(algo_chisqr(bigram)) + '\n')
                t.write("DICE:" + str(algo_Dice(bigram)) + '\n')



#print "-------------------------------------------------"
#print total_bigrams
#Problem 4 - 3
result_list = {}
measure = ["MIM", "EMIM", "CHISQR", "DICE"]
index = 0


def parse_dict(sorted_dict):
    res = ""
    for word, value in sorted_dict:
        res += word + ': ' + str(value) + ' '
    return res


for word in top_ten:
    key = ""
    mim = {}
    emim = {}
    chisqr = {}
    dice = {}

    for bigram, value in bsorted:
        line = str(bigram).split(' ')
        if word == line[0] or word == line[1]:
            if word != line[0]:
                key = line[0]
            else:
                key = line[1]
            #%0.3f formatting
            mim[key] = round(algo_MIM(bigram), 3)
            emim[key] = round(algo_EMIM(bigram), 3)
            chisqr[key] = round(algo_chisqr(bigram), 3)
            dice[key] = round(algo_Dice(bigram), 3)
    result_list[word] = [mim, emim, chisqr, dice]


with open("p4_3.txt","w") as p:
    for word in top_ten:
        list = result_list[word]
        for dict in list:
            dict_sort = sorted(dict.iteritems(), key=itemgetter(1), reverse=True)
            dict_sort = dict_sort[:5]

            print '%-6s %-6s %s' % (word, measure[index], parse_dict(dict_sort))
            p.write('%-6s %-6s %s\n' % (word, measure[index], parse_dict(dict_sort)))
            index += 1
        index = 0
print 'total bigrams:', total_bigrams, 'unique bigrams:', unique_bigram, '\n'
