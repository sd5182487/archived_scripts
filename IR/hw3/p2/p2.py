import math
from numpy import *
from collections import OrderedDict
import csv



users = []
movies = []
user_movie_score = {}
#movie_user_score = {}
user_movie = {}
#movie_user = {}
queries = []
A = []
cal_movie_rate = {}
opti_movie_rate = []
simi_moves = {}
movie_neighbours = {}


# cal Σi sqrt
def sqrt_sum(vector):
    res = 0
    for v in vector:
        res += v * v
    return math.sqrt(res)


# vector normalize
def normalize_vector(vector):
    tmp = []
    for v in vector:
        if v > 0:
            tmp.append(v)
    vec_len = sqrt_sum(tmp)
    if vec_len == 0:
        return []
    for i in range(0, len(tmp)):
        tmp[i] /= vec_len
    return tmp


#find score by pair(user,movie)
def get_score(uid, mid):
    try:
        s = user_movie_score[uid][mid]
    except:
        s = 0
    return s

print "merge csv file - new_train"
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
for row in reader:
    mid = int(row[0])
    uid = int(row[1])
    s = int(row[2]) - 2
    if uid not in user_movie:
        user_movie_score[uid] = {}
        user_movie[uid] = []
        users.append(uid)
    if mid not in movies:
        movies.append(mid)
        cal_movie_rate[mid] = 0
    user_movie_score[uid][mid] = s
    user_movie[uid].append(mid)
    cal_movie_rate[mid] += 1
users = sorted(users)
movies = sorted(movies)
f.close()

print "for each movie, cal sum of user rated this"
cal_movie_rate = sorted(cal_movie_rate.iteritems())
for pair in cal_movie_rate:
    opti_movie_rate.append(pair[1])

for i in range(0, len(movies)):
    mid = movies[i]
    simi_moves[mid] = {}
    movie_neighbours[mid] = []
mu_matrix = []

# get movie-user pair matrix
for mid in movies:
    row = []
    for uid in users:
        row.append(get_score(uid, mid))
    mu_matrix.append(row)
mu_matrix = mat(mu_matrix)
#transpose_mu_matrix = math.T(mu_matrix)
transpose_mu_matrix = mu_matrix.T
A = mu_matrix * transpose_mu_matrix
A = A.tolist()

# normalize movie-movie matrix A
for i in range(0, len(movies)):
    for j in range(0, len(movies)):
        A[i][j] = float(A[i][j]) / opti_movie_rate[i]

# if same, sim 0
for i in range(0, len(movies)):
    A[i][i] = float(0)

# cal similarity
for i in range(0, len(movies)):
    weights = A[i]
    tmp = {}
    for j in range(0, len(movies)):
        tmp[movies[j]] = weights[j]
    simi_moves[movies[i]] = tmp

# get top 5 similar movie for each movie
# modify the 5 to 3 to make it KNN,K = 3
for mid in movies:
    tmp_tuple = sorted(simi_moves[mid].iteritems(), key=lambda d: d[1], reverse=True)[:5]
    simi_moves[mid] = OrderedDict()
    for k in tmp_tuple:
        simi_moves[mid][k[0]] = k[1]
        movie_neighbours[mid].append(k[0])

# read queries
with open('dev.queries', 'r') as f:
    for line in f:
        elements = line.rstrip('\n').split(',')
        queries.append((int(elements[0]), int(elements[1])))

# Mean result
f = open('mean_predict', 'w')
for q in queries:
    mid = q[0]
    uid = q[1]
    try:
        movie_neighbour_now = movie_neighbours[mid]
    except:
        f.write('%d\n' % 2)
        continue
    sum_s = 0
    for neighbour in movie_neighbour_now:
        neighbour_score = get_score(uid, neighbour)
        sum_s += neighbour_score
    if sum_s > 0:
        predict_score = (float(sum_s) / len(movie_neighbour_now)) + 2
        f.write('%s\n' % str(predict_score))
    else:
        f.write('%d\n' % 2)
f.close()

# predict with weighted mean - result
f = open('weighted_mean_predict', 'w')
for q in queries:
    mid = q[0]
    uid = q[1]
    try:
        cur_movie_weight = simi_moves[mid]
        movie_neighbour_now = movie_neighbours[mid]
    except:
        f.write('%d\n' % 2)
        continue
    movie_weight = []
    for neighbour in cur_movie_weight:
        movie_weight.append(cur_movie_weight[neighbour])
    movie_weight = normalize_vector(movie_weight)
    if len(movie_weight) == 0:
        f.write('%d\n' % 2)
        continue
    predict_score = 0
    for i in range(0, len(movie_weight)):
        tmp = movie_weight[i] * get_score(uid, movie_neighbour_now[i])
        predict_score += tmp
    weight_sum = 0
    for w in movie_weight:
        weight_sum += w
    predict_score = predict_score / weight_sum + 2
    print predict_score
    f.write('%s\n' % str(predict_score))
f.close()