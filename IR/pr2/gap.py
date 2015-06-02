#!/usr/bin/python
from __future__ import division
import argparse
from collections import OrderedDict
import matplotlib.pyplot as plt
import math
#import xlrd
from scipy import stats

class qrel:
    """a class for parsing trec qrels"""

    def __init__(self, path, maxgrade=1):
        """constructor. Takes a path to a qrel file 
        and optionally the theoretically max grade, 
        which defaults to binary. Converts all neg. 
        grades to 0"""

        #store the maxgrade
        self.maxgrade = maxgrade

        #compute the score associated w/ each grade
        self.scores=[(2**x - 1)/(2**maxgrade) for x in range(maxgrade+1)]

        #the actual qrel dict of dicts
        #_qrel[query][doc] = grade
        self._qrel = dict()

        #the documents at each grade
        #dict of dicts of lists
        #R[query][grade] = count
        self.R = dict()

        #read the qrel one line at a time
        IN = open(path)
        for line in IN:
            row = line.strip().split()
            
            #cast stuff to ints
            query = row[0]
            doc = row[-2]
            grade = int(row[-1])
            
            #init dicts for that query
            if query not in self.R:
                self.R[query] = [0]*maxgrade
                self._qrel[query] = dict()

            #make sure grade is non-neg
            if grade < 0:
                grade = 0
            #if its rel add it to R
            if grade > 0:
                self.R[query][grade-1] += 1
            #add it to the qrel
            self._qrel[query][doc] = grade
        IN.close()

    def getR(self, query):
        """returns that queries dict of the docs at each grade"""
        return self.R[query]

    def getQueries(self):
        """returns the set of queries"""
        return self.R.keys()

    def judge(self, query, doc):
        """returns the grade of the doc for that query."""
        try:
            return self._qrel[query][doc]
        except KeyError:
            return 0

    def getScore(self, grade):
        """returns the score associated w/ a rel grade"""
        return self.scores[grade]

    def getMaxgrade(self):
        """returns the maxgrade in the qrel"""
        return self.maxgrade

def parserun(runpath, maxrank=20):
        """constructs a run from a trec run"""

        #initialize 
        #ranked lists go in a dict of lists
        #rl[query]=[doc1,doc2,...]
        rl = dict()

        name = None

        #read the ranked list into a dict of dicts
        #rawlist[query][doc]=score
        rawlist = dict()
        #open the run
        IN = open(runpath)
        #and read it line by line
        for line in IN.readlines():
            #chomp it and split it by white space
            row = line.strip().split()

            #make sure the row wasn't empty
            if len(row)==0:
                continue

            if name == None:
                name = row[-1]

            #read the query, doc, score, etc
            query = row[0]
            
            if row[-2] == 'NaN':
                score = 0.0
            else:
                score = float(row[-2])

            #make sure the query is in the dict
            if not query in rawlist:
                rawlist[query]=dict()

            #store the doc in the presorted list
            #if the doc shows up more than once in a query, 
            #that's not my problem

            doc = row[2]
            rawlist[query][doc] = score
        IN.close()

        #for each query 
        for query in sorted(rawlist):

            #sort the list by score and then by name
            rl[query] = sorted(rawlist[query],key=lambda x: (rawlist[query][x],x),reverse=True)[:maxrank]

        return name, rl

def gap(query,run,qrel):
    """gap of a run on a query given a qrel"""
    totalp=0
    for n in range(len(run[query])):
        docn = run[query][n]
        grade = qrel.judge(query,docn)
        if grade > 0:
            p = 0
            for m in range(n+1):
                i = min(grade, qrel.judge(query, run[query][m]))
                for j in range(1, i+1):
                    p += qrel.getScore(j)
            totalp += p / (n+1)
    denom = 0
    for i in range(1,qrel.getMaxgrade()+1):
        rel=0
        for j in range(1, i+1):
            rel += qrel.getScore(j) 
        denom += rel*qrel.R[query][i-1]
    return totalp/denom


def get_vectorQ(query, currun ,qrel):
    vectorQ = []
    for doc_name in currun[query]:
        vectorQ.append(qrel.judge(query, doc_name))
    return vectorQ


def get_recall_k(vec, R):
    krecall = []
    total = 0
    for v in vec:
        total += v
        krecall.append(float(total) / R)
    return krecall


def calR(query, qrel):
    rl = qrel.getR(query)
    related = 0
    for count in rl:
        related += count
    return related


def cal_F1(v, R):
    total = 0
    for fig in v:
        if fig > 0:
            total += 1
    recall = float(total) / R
    precision = total / len(v)
    return 2 * recall * precision / (recall + precision)


def cal_preck(v):
    preck_v = []
    score = 0
    for n in range(0, len(v)):
        if v[n] > 0:
            score += 1
        preck_v.append(float(score / (n + 1)))
    return preck_v


def cal_AvgP(prec, v ,R):
    total = 0
    for n in range(0, len(v)):
        if v[n] > 0:
            total += prec[n]
    return float(total / R)

def cal_idcg(q, qrel):
    q_qrel = qrel._qrel[q]
    ideal_v = []
    for elem in q_qrel:
        ideal_v.append(q_qrel[elem])
    return sorted(ideal_v, reverse=True)


def cal_DCG(v):
    total = 0
    if len(v) > 0:
        total += v[0]
        for n in range(1, len(v)):
            total += float(v[n]) / (math.log(n + 1, 2))
    return total


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('qrel_path', help='path to qrel file')
    parser.add_argument('run_path', help='path to run file')
    parser.add_argument('-v', '--verbose', help='display score for each query', action='store_true')
    parser.add_argument('-r', '--rank', type=int, help='evaluation rank. Defaults to 1000')
    parser.add_argument('-m', '--maxgrade', type=int, help='specify maxgrade. Defaults to 4')
    args = parser.parse_args()
    #get the maxgrade
    MAXGRADE = 4

    if args.maxgrade != None:
        MAXGRADE = args.maxgrade
    #so we can make the qrel
    theqrel = qrel(args.qrel_path, MAXGRADE)

    #theqrel = qrel('corpus.qrel', MAXGRADE)
    #now get the rank
    RANK = 400

    if args.rank != None:
        RANK = args.rank
    runname, currun = parserun(args.run_path, RANK)

    #runname, currun = parserun('run_bm25.txt', RANK)

    '''
    evaluation starts here: GP,AP,F1,NDCG
    '''
    mname = args.run_path[4:-4]
    #finally, do the evaluation
    with open('p2-scores.txt', 'a') as p2:
        mgap = 0
        for query in sorted(theqrel.getQueries()):
            qgap = gap(query, currun, theqrel)
            if args.verbose:
                p2.write("\t".join(['GAP', mname, query, str(qgap), '\n']))
            mgap += qgap
        mgap /= len(theqrel.getQueries())
        p2.write("\t".join(['GAP', 'avg', str(mgap), '\n']))

    #F1
        #print "this is f1"
        queries_vector = OrderedDict()
        for query in sorted(theqrel.getQueries()):
            queries_vector[query] = get_vectorQ(query, currun, theqrel)
        total = 0
        for query in queries_vector:
            vector = queries_vector[query]
            R = calR(query, theqrel)
            S = cal_F1(vector, R)
            p2.write("\t".join(['F1', mname, query, str(S), '\n']))
            total += S
        p2.write("\t".join(['F1', 'avg', str(total / 10), '\n']))

    # AP
        total = 0
        for query in queries_vector:
            R = calR(query, theqrel)
            vector = queries_vector[query]
            prec_k_vector = cal_preck(vector)
            S = cal_AvgP(prec_k_vector, vector, R)
            p2.write("\t".join(['AP', mname, query, str(S), '\n']))
            total += S
        p2.write("\t".join(['AP', 'avg', str(total / 10), '\n']))

    #NDCG
        total = 0
        for query in queries_vector:
            R = calR(query, theqrel)
            vector = queries_vector[query]
            ideal_vector = cal_idcg(query, theqrel)
            vector_dcg = cal_DCG(vector)
            ideal_vector_dcg = cal_DCG(ideal_vector)
            S = float(vector_dcg)/ideal_vector_dcg
            p2.write("\t".join(['NDCG', mname, query, str(S), '\n']))
            total += S
        p2.write("\t".join(['NDCG', 'avg', str(total / 10), '\n']))

    #this is plot
    R = calR('234', theqrel)
    vector = queries_vector['234']
    recall_k = get_recall_k(vector, R)
    prec_k = cal_preck(vector)
    #print recall_k
    #print prec_k

    if mname == 'bm25':
        plt.plot(recall_k, prec_k,'r')
        plt.savefig('bm25.png')
    elif mname == 'lap':
        plt.plot(recall_k, prec_k,'r')
        plt.savefig('lap.png')
    elif mname == 'jm':
        plt.plot(recall_k, prec_k,'r')
        plt.savefig('jm.png')



    '''
    t-test
    '''
    gapjm = [0.007092199, 0.416051848, 0.401073802, 0.328620692,
          0.128821049, 0.08681768, 0.39754515, 0.159366648, 0.073421734, 0.078979815, 0.207779062]
    gapbm = [0.004950495, 0.514717555, 0.489986955, 0.471946488, 0.187050178, 0.296786684,
          0.589140302, 0.267719369, 0.111371842, 0.354945078, 0.328861495]
    apjm = [0.007092199,0.577582616,0.617789087,0.431904665,0.195884238,0.083632273,0.359649184,0.183296237,0.112281649,0.072171725]
    apbm = [0.004950495,0.745847977,0.800163029,0.719118415,0.23305121,0.332150429,0.599650636,0.30499938,0.202440645,0.295213168]
    f1jm = [0.004987531,0.654723127,0.696183206,0.531604538,0.191111111,0.138084633,0.504409171,0.301886792,0.223628692,0.080952381]
    f1bm = [0.004987531,0.697068404,0.778625954,0.696920583,0.2,0.218262806,0.589065256,0.322851153,0.312236287,0.095238095]
    ndjm = [0.140064823,0.733003923,0.747687441,0.6304568,0.488460127,0.315320848,0.660267122,0.553450661,0.339092035,0.349417395]
    ndbm = [0.130578791,0.816944631,0.827579147,0.814416582,0.543688816,0.697472281,0.827211334,0.660727704,0.4839144,0.618220947]

    #print jm
    #print bm
    with open("p2-tests.txt", 'w') as pt:
        gpresult = stats.ttest_ind(gapjm, gapbm, equal_var=True)
        apresult = stats.ttest_ind(apjm,apbm,equal_var=True)
        f1result = stats.ttest_ind(f1jm,f1bm,equal_var=True)
        ndresult = stats.ttest_ind(ndjm,ndbm,equal_var=True)
        pt.write("\t".join(['gp', str(gpresult), '\n']))
        pt.write("\t".join(['ap', str(apresult), '\n']))
        pt.write("\t".join(['F1', str(f1result), '\n']))
        pt.write("\t".join(['NDCG', str(ndresult), '\n']))
    #    with open('test.txt', 'a')
