import math
from numpy import *
from collections import OrderedDict
import csv


users = []
movies = []
user_movie_score = {}
movie_user_score = {}
user_movie = {}
movie_user = {}
u_simi = {}
u_neighbour = {}
queries = []
user_vector = {}
user_vector_ss = {}

# cal Σi sqrt
def sqrt_sum(vector):
    res = 0
    for v in vector:
        res += v * v
    return math.sqrt(res)


# vector multi
def vector_multiply(a, b):
    res = 0
    for i in range(0, len(a)):
        res += a[i] * b[i]
    return res


#find score by pair
def get_score(uid, mid):
    try:
        s = user_movie_score[uid][mid]
    except:
        s = 0
    return s


# vector normalize
def normalize_vector(vector):
    vec_len = sqrt_sum(vector)
    if vec_len == 0:
        return []
    for i in range(0, len(vector)):
        vector[i] /= vec_len
    return vector

print "merge csv file - new_train "
with open('new_train.csv', 'w') as f:
    with open('train.csv', 'r') as t:
        for line in t:
            f.write(line)
    with open('dev.csv', 'r') as t:
        for line in t:
            f.write(line)
    with open('test.csv', 'r') as t:
        for line in t:
            f.write(line)

print "read and store merged file"
f = open('new_train.csv', 'rb')
reader = csv.reader(f)
i = 0
for row in reader:
    mid = int(row[0])
    uid = int(row[1])
    s = int(row[2]) - 2
    if uid not in user_movie:
        user_movie_score[uid] = {}
        user_movie[uid] = []
        users.append(uid)
    if mid not in movie_user:
        movie_user_score[mid] = {}
        movie_user[mid] = []
        movies.append(mid)
    user_movie_score[uid][mid] = s
    movie_user_score[mid][uid] = s
    user_movie[uid].append(mid)
    movie_user[mid].append(uid)
    print i
    i += 1
users = sorted(users)
movies = sorted(movies)
f.close()

print "for each user, calculate it's vector"
print "for each vector, calculate it's length"
for uid in users:
    vector = []
    for mid in movies:
        vector.append(get_score(uid, mid))
    user_vector[uid] = vector
    user_vector_ss[uid] = sqrt_sum(vector)

print "calculate user weight"
for i in range(0, len(users)):
    uid = users[i]
    u_simi[uid] = {}
    u_neighbour[uid] = []

for i in range(0, len(users) - 1):
    active_user_id = users[i]
    auv_ss = user_vector_ss[active_user_id]
    active_user_movie = user_movie[active_user_id]
    for j in range(i + 1, len(users)):
        other_user_id = users[j]
        ouv_ss = user_vector_ss[other_user_id]
        other_user_movie = user_movie[other_user_id]
        common_movie = list(set(active_user_movie) & set(other_user_movie))
        tmp = 0
        for mid in common_movie:
            active_user_score = get_score(active_user_id, mid)
            other_user_score = get_score(other_user_id, mid)
            tmp += active_user_score * other_user_score
        if tmp == 0:
            cos_similarity = 0
        else:
            cos_similarity = tmp / (auv_ss * ouv_ss)
        u_simi[active_user_id][other_user_id] = cos_similarity
        u_simi[other_user_id][active_user_id] = cos_similarity
    print i

print "for recorded user similarity, get top 5"
# modify the 5 to 3 to make it KNN,K = 3
for uid in users:
    tmp_tuple = sorted(u_simi[uid].iteritems(), key=lambda d: d[1], reverse=True)[:5]
    u_simi[uid] = OrderedDict()
    for t in tmp_tuple:
        u_simi[uid][t[0]] = t[1]
        u_neighbour[uid].append(t[0])

print "store all queries"
with open('dev.queries', 'r') as f:
    for line in f:
        elements = line.rstrip('\n').split(',')
        queries.append((int(elements[0]), int(elements[1])))

print "mean predict"
f = open('mean_res.txt', 'w')
for query in queries:
    mid = query[0]
    uid = query[1]
    try:
        cur_u_neighbour = u_neighbour[uid]
    except:
        f.write('%d\n' % 2)
        continue
    score_sum = 0
    for neighbour in cur_u_neighbour:
        neighbour_score = get_score(neighbour, mid)
        score_sum += neighbour_score
    if score_sum > 0:
        predict_score = (float(score_sum) / len(cur_u_neighbour)) + 2
        f.write('%s\n' % str(predict_score))
    else:
        f.write('%d\n' % 2)
f.close()

print "weighted mean predict"
f = open('weighted_mean_res.txt', 'w')
for query in queries:
    mid = query[0]
    uid = query[1]
    try:
        cur_user_weight = u_simi[uid]
        cur_u_neighbour = u_neighbour[uid]
    except:
        f.write('%d\n' % 2)
        continue
    user_weight = []
    for neighbour in cur_user_weight:
        user_weight.append(cur_user_weight[neighbour])
    user_weight = normalize_vector(user_weight)
    if len(user_weight) == 0:
        f.write('%d\n' % 2)
        continue
    predict_score = 0
    for i in range(0, len(cur_u_neighbour)):
        predict_score += user_weight[i] * get_score(cur_u_neighbour[i], mid)
    weight_sum = 0
    for w in user_weight:
        weight_sum += w
    predict_score = predict_score / weight_sum + 2
    f.write('%s\n' % str(predict_score))
f.close()