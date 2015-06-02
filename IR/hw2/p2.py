#!/usr/bin/python

from math import log10, pow
from numpy import linalg, array, ones


total_word = 0
unique_word = 0
words = []
px = []
py = []
result = open("output.txt").read().split()
for word in result:
    if word not in words:
        unique_word += 1
        words.append(word)
    total_word += 1
    px.append(log10(total_word))
    py.append(log10(unique_word))



Array = array([px, ones(total_word)])
beta, k = linalg.lstsq(Array.T, py)[0]
k = pow(10, k)
print "beta: ", beta
print "k: ", k