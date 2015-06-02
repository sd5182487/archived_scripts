#!/usr/bin/python
#from time import time
from operator import itemgetter


def fetcher():
    unique_word = 0
    dic = []
    count = {}
    result = open('output.txt').read().split()
    total_words = len(open('output.txt').readlines())
    for word in result:
        if count.has_key(word):
            count[word] = count[word] + 1
        else:
            unique_word += 1
            count[word] = 1



    lsorted = sorted(count.items(), key=itemgetter(1), reverse=True)
    rank = 0
    index = 0
    findex = 0
    print '%-10s %-10s %-5s %-18s %-10s' % ("word", "frequency", "rank", "probability", "rank*probability")
    for (value, times) in lsorted:
        rank += 1
        prob = float(times)/total_words
        current = (value, times, rank, prob, rank*prob)
        dic.append(current)
        if index < 25:
            print '%-10s %-10s %-5s %-18s %-10s' % (value, times, rank, prob, rank*prob)
            index += 1
        elif findex < 25 and value[0] == 'f':
            print '%-10s %-10s %-5s %-18s %-10s' % (value, times, rank, prob, rank*prob)
            findex += 1


    #total num of words and unique words
    print "\n"
    print "There's", str(unique_word), "unique words in Alice's Wonderland"
    print "There's", total_words, "total words"

    #word frequency
    with open("word_prob.txt","w") as wp:
        for v in dic:
            wp.write(str(v[3])+"\n")

    with open("product.txt", "w") as p:
        for v in dic:
            p.write(str(v[4])+"\n")

    with open("omit.txt", "w") as o:
        for v in dic:
            if v[1] < 5:
                o.write(str(v[1])+"\n")

#    sums = open("omit.txt").readlines()
#    total = 0
#    for line in sums:
#        total = total + int(line)
#    print total

if __name__ == '__main__':
#    t1 = time()
    fetcher()
