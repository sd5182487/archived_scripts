#!/usr/bin/python
__author__ = 'haohuang'
# This version is constant memory before I sort the terms
# In order to realize p2 constant memory, I did an extra sort here
#
import os
from os import listdir
from os.path import isfile, join
from collections import OrderedDict
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer
from nltk import clean_html


class Tokenizer:
    def __init__(self, path):
        self.directory = path       # refer to this directory
        self.terms = OrderedDict()  # here's the sorted terms i mentioned
        self.term_id = 0

# tokenize execution function
    def exe(self):
        if isfile('docids.txt'):
            os.remove('docids.txt')
        doc_id = 0
        for path in listdir(self.directory):
            if isfile(join(self.directory, path)):
                with open(join(self.directory, path), "r") as f:
                    content = str(f.read())
                    index = content.find('HTTP/')
                    content = content[index:]
                    index = content.find('\r\n\r\n')
                    content = content[index:]
                    self.text = clean_html(content)   #get clean html
                positions = self.get_tokens()
                with open("docids.txt", "a") as did:
                    did.write('%s\t%d\n' % (path, doc_id))
                with open("doc_index_unsorted.txt", "a") as usdi:
                    for term in positions:
                        usdi.write('%d\t%d' % (doc_id, self.terms[term]))
                        for pos in positions[term]:
                            usdi.write('\t' + str(pos))
                        usdi.write('\n')
                doc_id += 1
        with open("termids.txt", "w") as f:
            for term in self.terms:
                f.write('%s\t%d\n' % (term.encode('utf-8'), self.terms[term]))
        term_w_offset = []          #new dic with term's offset

        with open('termids.txt', 'r') as tid:
            for lines in tid:
                term_w_offset.append([])
        offset = 0

        #construct a file with offset so I can directly seek and fetch later
        with open('doc_index_unsorted.txt', 'r') as dius:
            for line in dius:
                elements = line.split('\t')
                term_w_offset[int(elements[1])].append(offset)
                offset += len(line)

        with open('doc_index_unsorted.txt', 'r') as f_un, open('doc_index.txt', 'w') as f_di:
            for term_id in range(0, len(term_w_offset)):
                for offset in term_w_offset[term_id]:
                    f_un.seek(offset)
                    line = f_un.readline()
                    f_di.write(line)
        os.remove('doc_index_unsorted.txt')

    def get_tokens(self):
        porter = PorterStemmer()
        positions = OrderedDict()
        pos = 1
        tk = RegexpTokenizer(r'\w+(\.?\w+)*')
        tokens = tk.tokenize(self.text)
        if tokens:
            for token in tokens:
                token = token.lower()
                if token in stopterm:  #regards the stoplist
                    pos += 1
                    continue
                token = porter.stem(token)
                try:
                    token = token.encode('utf-8')  #trans to utf-8
                except:
                    pos += 1
                    continue
                else:
                    if token not in self.terms:
                        self.terms[token] = self.term_id
                        self.term_id += 1
                    if token not in positions:
                        positions[token] = [pos]
                    else:
                        positions[token].append(pos)
                pos += 1
        return positions


if __name__ == "__main__":
    global stopterm
    global term_id
    term_id = 0
    with open("stoplist.txt", "r") as s:
        stopterm = s.readlines()
        for word in stopterm:
            word = word.rstrip('\n')
    tk = Tokenizer("corpus")
    tk.exe()