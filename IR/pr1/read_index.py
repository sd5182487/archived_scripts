import sys
from nltk.stem.porter import PorterStemmer


####helper functions

# get docid by doc name else return -1
def get_docid(doc):
    with open("docids.txt", "r") as did:
        for line in did:
            line = line.strip('\n')
            tmp = line.split('\t')
            if tmp[0] == doc:
                return tmp[1]
        return -1


#get termid by term name , else -1
def get_termid(term):
    with open("termids.txt", "r") as tid:
        for line in tid:
            line = line.strip('\n')
            tmp = line.split('\t')
            if tmp[0] == term:
                return tmp[1]
        #print "term not found, please check spelling"
        return -1


#function for cmd option --doc "docname"

def get_doc_info(doc):
    doc_id = get_docid(doc)
    if doc_id == -1:
        print "invalid document name %s, please check your spelling" % doc
        return
    print "Listing for document: " + doc
    print "DOCID: " + doc_id
        
    with open("doc_index.txt", "r") as din:
        uniq_terms = 0
        total_terms = 0
        for line in din:
            line = line.strip('\n')
            tmp = line.split('\t')
            if tmp[0] == doc_id:
                total_terms += len(tmp) - 2        #exclude docid and term
                uniq_terms += 1
        print "Distinct terms: %s" % uniq_terms
        print "Total terms: %s" % total_terms


# function for cmd option --term TERM
def get_term_info(term):
    p = PorterStemmer()
    term = p.stem(term.lower())
    term_id = get_termid(term)
    if term_id == -1:
        print "term %s not found, please check spelling" % term
        return
    print "Listing for term: " + term
    print "TERMID: " + term_id

    with open("term_info.txt", "r") as t:
        for line in t:
            line = line.strip('\n')
            tmp = line.split('\t')
            if tmp[0] == term_id:
                print "Number of documents containing term: " + tmp[3]
                print "Term frequency in corpus: " + tmp[2]
                print "Inverted list offset: " + tmp[1]
                return


#function for cmd option --doc and --term
def get_inverted_list(doc, term):
    p = PorterStemmer()
    term = p.stem(term.lower())             #sort
    print "Inverted list for term: " + term
    print "In document: " + doc
    term_id = get_termid(term)
    if term_id == -1:
        print "Term %s not found, please check spelling" % doc
        return
    print "TERMID: " + term_id
    
    doc_id = get_docid(doc)
    if doc_id == -1:
        print "document not found"
        return
    print "DOCID: " + doc_id

    offset = -1
    with open("term_info.txt", "r") as f:
        for line in f:
            line = line.strip('\n')
            tmp = line.split('\t')
            if tmp[0] == term_id:
                offset = int(tmp[1])
                break
    if offset == -1:
        print "term id %s not found in term_info.txt" % term_id
        return
    
    with open("term_index.txt", "r") as t:
        t.seek(offset)
        line = t.readline()
        tcount = 0
        tmp = line.strip('\n').split('\t')
        doc_id_tmp = 0
        positions = []
        for i in range(1, len(tmp)):
            doc_id_tmp += int(tmp[i].split(':')[0])
            if doc_id_tmp == int(doc_id):
                tcount += 1
                positions.append(int(tmp[i].split(':')[1]))
            elif doc_id_tmp > int(doc_id):
                break
        if not positions:
            print "term id %s is not found for doc id %s in term_index.txt" % (term_id, doc_id)
            return
        print "Term tcount in document: ", tcount
        print "Positions:",
        prev_pos = 0
        if len(positions) > 1:
            for p in positions[0:-1]:
                print "%d," % (p + prev_pos),
                prev_pos = p + prev_pos
            print "%d" % (positions[-1] + prev_pos)
            


    
if __name__ == "__main__":
    if len(sys.argv) == 3:
        if sys.argv[1] == "--doc":
            get_doc_info(sys.argv[2])
        elif sys.argv[1] == "--term":
            get_term_info(sys.argv[2])
        else:
            print "invalid options please check."
    elif len(sys.argv) == 5:
        if sys.argv[1] == "--doc" and sys.argv[3] == "--term":
            get_inverted_list(sys.argv[2], sys.argv[4])
        elif sys.argv[1] == "--term" and sys.argv[3] == "--doc":
            get_inverted_list(sys.argv[4], sys.argv[2])
        else:
            print "invalid options"
    else:
        print "invalid options"

    #get_doc_info('clueweb12-0008wb-31-23874')
    #get_term_info('health')
    get_inverted_list('clueweb12-0008wb-31-23874', 'green')