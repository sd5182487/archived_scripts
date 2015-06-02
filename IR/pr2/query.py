#!/usr/bin/python

import sys
from lxml import etree
from nltk.tokenize import RegexpTokenizer
from nltk.stem.porter import PorterStemmer
import math


# query stemmer
def query_stem(query, queries_len):
    """
    store len(query) into queries_len as queries_len[query]
    return new_query, which is {term : occurance}

    """
    len = 0
    new_queries = {}
    porter = PorterStemmer()
    tokenizer = RegexpTokenizer(r'\w+(\.?\w+)*')
    token = tokenizer.tokenize(query)
    for tt in token:
        tt = tt.lower()                    # lowercase
        if tt in stopwords:
            continue                       # respect stopwords
        tt = porter.stem(tt)               # stemming
        if tt in new_queries:
            new_queries[tt] += 1
        else:
            new_queries[tt] = 1
        len += 1
    queries_len[query] = len
    return new_queries


# make a dictionary of queries
def get_query(context):
    queries = []
    for event, phrase in context:
        queries.append(phrase.text)
        phrase.clear()
        while phrase.getprevious() is not None:
            del phrase.getparent()[0]
    del context
    return queries


# get topic number
def get_topic_number(context):
    topic_num = []
    for event, phrase in context:
        topic_num.append(phrase.get("number"))
        phrase.clear()
        while phrase.getprevious() is not None:
            del phrase.getparent()[0]
    del context
    return topic_num


def get_termids(query):
    """
    given query, which is a list of terms,
    return {term:termid}
    
    """
    with open("termids.txt", "r") as t:
        terms = {}
        for line in t:
            tmp = line.strip('\n').split('\t')
            if tmp[0] in query:
                terms[tmp[0]] = tmp[1]
    return terms


def read_docs(file):
    """
    return document infos in format {doc_id:doc_name}
    and total number of docs

    """
    with open(file, "r") as f:
        doc_num = 0
        docs = {}
        for line in f:
            doc_num += 1
            tmp = line.strip('\n').split('\t')
            doc_id = int(tmp[1])
            doc_name = tmp[0]
            docs[doc_id] = doc_name
    return docs, doc_num


def cal_term_frequency(query, term_frequency):
    """
    calculate term frequency in all docs
    
    """
    terms = get_termids(query)
    for term in terms:
        term_id = terms[term]
        if term_id not in term_frequency:
            freq = cal_term_frequency_helper(term_id)
            term_frequency[term_id] = freq 


def cal_term_frequency_helper(term_id):
    """
    return term frequency(times) in all docs
    {doc_id:frequence_in_this_doc}
    
    """
    offset = -1
    with open("term_info.txt", "r") as t:
        for line in t:
            line = line.strip('\n')
            tmp = line.split("\t")
            if tmp[0] == term_id:
                offset = int(tmp[1])
                break
    if offset == -1:
        return {}
    with open("term_index.txt", "r") as f:
        f.seek(offset)
        line = f.readline()
        frequency = {}
        tmp = line.strip('\n').split('\t')
        doc_id = 0
        freq_tmp = 0
        
        for i in range(1, len(tmp)):
            if not tmp[i]:
                continue
            doc_id_tmp = int(tmp[i].split(':')[0])
            if i == 1:
                doc_id = doc_id_tmp
                freq_tmp = 1
                continue
            if doc_id_tmp == 0:
                freq_tmp += 1
                if i == len(tmp)-1:
                    frequency[doc_id] = freq_tmp 
            else:
                frequency[doc_id] = freq_tmp
                doc_id = doc_id_tmp + doc_id
                freq_tmp = 1                    # next doc start
    return frequency
    

def cal_doc_term(doc_len, total_doc):
    """
    Calculate total terms(stopwords applied) and return the average term per doc.
    
    """
    with open("doc_index.txt", "r") as f:
        sum_term = 0
        total_terms = 0
        prev_doc_id = 0
        for line in f:
            line = line.strip('\n')
            tmp = line.split('\t')
            sum_term += len(tmp) - 2
            if int(tmp[0]) == prev_doc_id:
                total_terms += len(tmp) - 2
            else:
                prev_doc_id = tmp[0]
                doc_len.append(total_terms)
                total_terms = len(tmp) - 2
        doc_len.append(total_terms)
        avg_term_d = float(sum_term) / total_doc
    return avg_term_d


def cal_vocabulary_size():
    v = 0
    # wc -l termids.txt
    with open("termids.txt", "r") as t:
        for line in t:
            v += 1
    return v


def cal_query_vector(terms, query_len):
    """
    terms:  {term:frequency_in_query}
    
    """
    q = []
    for term in terms:
        tf = terms[term]
        qi = tf / (tf + 0.5 + 1.5 * query_len / avg_query_len)
        q.append(qi)
    return q


def sqrt_sum(vec):
    tmp = 0
    for i in vec:
        tmp += i * i
    return math.sqrt(tmp)


def vector_multiply(a, b):
    result = 0
    for i in range(0, len(a)):
        result += a[i] * b[i]
    return result


def print_miss_query(topic):
    """
    all documents score are 0 if query has no term in corpus.
    
    """
    with open("docids.txt", "r") as f:
        for line in f:
            tmp = line.strip('\n').split('\t')
            doc_name = tmp[1]
            print ("%s\t%d\t%s\t%d\t%f\t%s" % (topic, 0, doc_name, k+1, 0, "run1"))


# okapi tf function
def tf(query, q, doc_len, avg_term_d, docs, term_frequency):
# query:  {term:frequency_in_query}
    terms = get_termids(query)    # {term:term_id}
    score = {}
    for doc_id in docs:
        doc_name = docs[doc_id]
        d = cal_d(terms, doc_id, doc_len, avg_term_d, term_frequency)
        if sqrt_sum(d) == 0 or sqrt_sum(q) == 0:
            score[doc_name] = 0
        else:
            s = vector_multiply(d, q) / (sqrt_sum(d) * sqrt_sum(q))
            score[doc_name] = s
    return score


def cal_d(terms, doc_id, doc_len, avg_term_d, term_frequency):
    """
    return doc vector of doc_id related to query terms for tf

    """
    d = []
    for term in terms:
        if doc_id in term_frequency[terms[term]]:
            tf = term_frequency[terms[term]][doc_id]
        else:
            tf = 0
        di = tf / (tf + 0.5 + 1.5 * doc_len[doc_id] / avg_term_d)
        d.append(di)
    return d


def tf_idf(query, q, doc_len, avg_term_d, total_doc, docs, term_frequency):
    terms = get_termids(query)
    score = {}
    for doc_id in docs:
        doc_name = docs[doc_id]
        d = idf_cal_d(terms, doc_id, doc_len, avg_term_d, total_doc, term_frequency)
        if sqrt_sum(d) == 0 or sqrt_sum(q) == 0:
            score[doc_name] = 0
        else:
            s = vector_multiply(d, q) / (sqrt_sum(d) * sqrt_sum(q))
            score[doc_name] = s
    return score


def idf_cal_d(terms, doc_id, doc_len, avg_term_d, total_doc, term_frequency):
    """
    return doc vector of doc_id related to query terms for tf-idf

    """
    d = []
    for term in terms:
        term_id = terms[term]
        if doc_id in term_frequency[term_id]:
            tf = term_frequency[term_id][doc_id]
        else:
            tf = 0
        df = len(term_frequency[term_id])
        di = tf / (tf + 0.5 + 1.5 * doc_len[doc_id] / avg_term_d) * math.log(float(total_doc) / df, 2)
        d.append(di)
    return d


def bm25(query, doc_len, avg_term_d, k1, k2, b, total_doc, docs, term_frequency):
    terms = get_termids(query)
    score = {}
    for doc_id in docs:
        doc_name = docs[doc_id]
        K = k1 * ((1-b) + b*doc_len[doc_id] / avg_term_d)
        elem = bm25_helper(terms, K, k1, k2, doc_id, total_doc, query, term_frequency)
        s = 0
        for e in elem:
            s += e
        score[doc_name] = s
    return score


def bm25_helper(terms, K, k1, k2, doc_id, total_doc, query, term_frequency):
    elem = []
    for term in terms:
        term_id = terms[term]
        df = len(term_frequency[term_id])
        if doc_id in term_frequency[term_id]:
            tfd = term_frequency[term_id][doc_id]
        else:
            tfd = 0

        tfq = query[term]
        if tfd == 0:
            elem.append(0)
        else:
            tmp = math.log((total_doc + 0.5) / (df + 0.5), 2) * (1.0 + k1) * tfd \
                / (K + tfd) * (1.0 + k2) * tfq / (k2 + tfq)
            elem.append(tmp)
    return elem


def laplace(query, doc_len, docs, term_frequency):
    terms = get_termids(query)
    vsize = cal_vocabulary_size()
    score = {}
    for doc_id in docs:
        score_tmp = 0
        doc_name = docs[doc_id]
        p = cal_laplace_p(terms, doc_id, doc_len[doc_id], vsize, term_frequency)
        for pi in p:
            score_tmp += math.log(pi, 2)
        score[doc_name] = score_tmp
    return score

    
def cal_laplace_p(terms, doc_id, doc_len, vsize, term_frequency):
    p = []
    for term in terms:
        if doc_id in term_frequency[terms[term]]:
            tf = term_frequency[terms[term]][doc_id]
        else:
            tf = 0

        p.append(float(tf + 1) / (doc_len + vsize))
    return p
            

# JM functions
def jm(query, doc_len, docs, term_frequency, lamb):
    terms = get_termids(query)
    score = {}
    for doc_id in docs:
        score_tmp = 0
        doc_name = docs[doc_id]
        p = cal_jm_p(terms, doc_id, doc_len, term_frequency, lamb)
        for pi in p:
            score_tmp += math.log(pi, 2)
        score[doc_name] = score_tmp
    return score

    
def cal_jm_p(terms, doc_id, doc_len, term_frequency, lamb):
    p = []
    for term in terms:
        term_id = terms[term]
        if doc_id in term_frequency[term_id]:
            tf = term_frequency[term_id][doc_id]
        else:
            tf = 0
        pdi = lamb * float(tf)/doc_len[doc_id] + (1-lamb) * second_term(term_frequency[term_id], doc_len)
        p.append(pdi)
    return p


def second_term(frequency, doc_len):
    sum_tmp = 0
    for f in frequency:
        sum_tmp += float(frequency[f]) / doc_len[f]
    return sum_tmp

if __name__ == '__main__':
    global avg_query_len
    avg_query_len = 0
    score_func = ["TF", "TF-IDF", "BM25", "Laplace", "JM"]
    if len(sys.argv) != 3 or sys.argv[1] != '--score':
        print "option format help: ./query.py --score <parameter>"
    elif sys.argv[2] not in score_func:
        print "scoring option name is invalid."
        print "valid scoring options:"
        for sf in score_func:
            print sf, ",",
        print 
    else:
        global stopwords
        with open("stoplist.txt", "r") as f:
            stopwords = f.readlines()
            stopwords = map(lambda sw: sw.strip('\n'), stopwords)
        doc_len = []            # total terms in each document
        docs, total_doc = read_docs("docids.txt")
        avg_term_d = cal_doc_term(doc_len, total_doc)
        context = etree.iterparse('topics.xml', events=('end',), tag='query')
        context2 = etree.iterparse('topics.xml', events=('end',), tag='topic')
        topics = get_topic_number(context2)
        queries_len = {}
        queries = get_query(context)
        list_of_terms = []
        for qu in queries:
            qu_list = query_stem(qu, queries_len)
            list_of_terms.append(qu_list)
        i = 0
        sum_query_len = 0
        for ql in queries_len:
            sum_query_len += queries_len[ql]
            i += 1
        avg_query_len = float(sum_query_len) / i

        term_frequency = {}
        for j in range(0, len(list_of_terms)):
            cal_term_frequency(list_of_terms[j], term_frequency)
        
        if sys.argv[2] == "TF":
            for j in range(0, len(list_of_terms)):
                if not list_of_terms[j]:  # if the query is a non-term query, e.g, only contains stopword
                    print_miss_query(topics[j])
                    continue
                q = cal_query_vector(list_of_terms[j], queries_len[queries[j]])
                score = tf(list_of_terms[j], q, doc_len, avg_term_d, docs, term_frequency)
                score = sorted(score.items(), key=lambda s: s[1],reverse=True)
                for k in range(0, len(score)):
                    print ("%s\t%d\t%s\t%d\t%f\t%s" % (topics[j], 0, score[k][0], k+1, score[k][1], "run1"))
                        
        elif sys.argv[2] == "TF-IDF":
            for j in range(0, len(list_of_terms)):
                if not list_of_terms[j]:  # if the query is a non-term query, e.g, only contains stopword
                    print_miss_query(topics[j])
                    continue
                #print "********************"
                q = cal_query_vector(list_of_terms[j], queries_len[queries[j]])
                score = tf_idf(list_of_terms[j], q, doc_len, avg_term_d, total_doc, docs, term_frequency)
                score = sorted(score.items(), key=lambda s: s[1],reverse=True)
                for k in range(0, len(score)):
                    print ("%s\t%d\t%s\t%d\t%f\t%s" % (topics[j], 0, score[k][0], k+1, score[k][1], "run1"))

        elif sys.argv[2] == "BM25":
            k1 = 1.2
            k2 = 100
            b = 0.75
            for j in range(0, len(list_of_terms)):
                score = bm25(list_of_terms[j], doc_len, avg_term_d, k1, k2, b, total_doc, docs, term_frequency)
                score = sorted(score.items(), key=lambda s: s[1],reverse= True)
                for k in range(0, len(score)):
                    print ("%s\t%d\t%s\t%d\t%f\t%s" % (topics[j], 0, score[k][0], k+1, score[k][1], "run1"))
                    
        elif sys.argv[2] == "Laplace":
            for j in range(0, len(list_of_terms)):
                score = laplace(list_of_terms[j], doc_len, docs, term_frequency)
                score = sorted(score.items(), key=lambda s: s[1],reverse=True)
                for k in range(0, len(score)):
                    print ("%s\t%d\t%s\t%d\t%f\t%s" % (topics[j], 0, score[k][0], k+1, score[k][1], "run1"))            

        elif sys.argv[2] == "JM":
            lamb = 0.2     # 0 <= lamb <= 1
            for j in range(0, len(list_of_terms)):
                score = jm(list_of_terms[j], doc_len, docs, term_frequency, lamb)
                score = sorted(score.items(), key=lambda s: s[1],reverse=True)
                for k in range(0, len(score)):
                    print ("%s\t%d\t%s\t%d\t%f\t%s" % (topics[j], 0, score[k][0], k+1, score[k][1], "run1"))



