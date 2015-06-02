#!/usr/bin/python
import sys
from os import listdir
from os.path import isfile, join
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer
from nltk import clean_html


class Tokenizer:
    directory = ""
    text = ""
    terms = {}

    def __init__(self, path):
        self.directory = path

    def get_tokens(self):
        global term_id
        porter = PorterStemmer()
        positions = {}
        pos = 1
        tokenizer = RegexpTokenizer(r'\w+(\.?\w+)*')
        tokens = tokenizer.tokenize(self.text)
        if tokens:
            for token in tokens:
                token = token.lower()
                if token in stopwords:
                    pos += 1                      # calculate positions
                    continue                      # apply stopwords
                token = porter.stem(token)        # lowercase and stemming
                if token not in self.terms:       # calculate term_id
                    self.terms[token] = term_id
                    term_id += 1
                if token not in positions:
                    positions[token] = [pos]
                else:
                    positions[token].append(pos)
                pos += 1
        return positions

    def exe(self):
        doc_id = 0
        for path in listdir(self.directory):
            if isfile(join(self.directory, path)):
                with open(join(self.directory, path), "r") as f:
                    content = str(f.read())
                    index = content.find('HTTP/')
                    content = content[index:]
                    index = content.find('\r\n\r\n')
                    content = content[index:]
                    #get clean content
                    self.text = clean_html(content)
                #constant memory #only term grows
                positions = self.get_tokens()

                with open("docids.txt", "a") as id:
                    id.write(str(doc_id) + "\t" + path + "\n")

                with open("doc_index.txt", "a") as idx:
                    for term in positions:
                        idx.write(str(doc_id) + '\t' + str(self.terms[term]))
                        for pos in positions[term]:
                            idx.write('\t' + str(pos))
                        idx.write('\n')
                doc_id += 1

        with open("termids.txt", "w") as f:
            for term in self.terms:
                try:
                    f.write(str(self.terms[term]) + '\t')
                    f.write(term.encode('utf-8'))
                    f.write('\n')
                except:
                    print "terminated Ill be back"

if __name__ == "__main__":
    global stopwords
    global term_id
    term_id = 0
    with open("stoplist.txt", "r") as s:
        stopwords = s.readlines()
        for word in stopwords:
            word = word.rstrip('\n')
    #stopwords = map(lambda sw: sw.strip('\n'), stopwords)
    # if len(sys.argv) != 2:
    #     print "usage: python Tokenizer.py <directory_name>"
    #     sys.exit()
    # token = Tokenizer(sys.argv[1])
    tokenizer = Tokenizer("corpus")
    tokenizer.exe()
