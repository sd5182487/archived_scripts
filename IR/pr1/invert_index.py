#!/usr/bin/python
## CS 6200 IR
## Hao Huang

with open('doc_index.txt', 'r') as did, open('term_index.txt', 'w') as tid, open('term_info.txt', 'w') as tinfo:
    cur_doc_id = 0
    cur_term_id = 0
    last_doc_id = 0
    last_term_id = 0
    count_doc = 0
    count_term = 0

    tinfo.write("%d\t%d\t" % (cur_term_id, tid.tell()))
    tid.write('%d' % cur_term_id)
    for line in did:
        record = line.strip('\n').split('\t')
        record = [int(x) for x in record]
        cur_doc_id = record[0]
        cur_term_id = record[1]

        if last_term_id != cur_term_id:
            tinfo.write("%d\t%d\n" % (count_term, count_doc))
            last_doc_id = 0
            count_term = 0
            count_doc = 0

            tid.write('\n')
            tinfo.write("%d\t%d\t" % (cur_term_id, tid.tell()))
            tid.write('%d' % cur_term_id)

        count_doc += 1
        pos = record[2:]
        count_term += len(pos)
        for i in range(len(pos)-1, 0, -1):
            pos[i] -= pos[i-1]
        doc_offset = cur_doc_id - last_doc_id   #calculating position

        tid.write('\t%d:%s' % (doc_offset, pos[0]))
        for p in range(1, len(pos)):
            tid.write('\t%d:%s' % (0, pos[p]))
        last_doc_id = cur_doc_id
        last_term_id = cur_term_id
    tinfo.write("%d\t%d" % (count_term, count_doc))