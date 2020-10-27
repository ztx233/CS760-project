import pandas as pd
from scipy import sparse as sp
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

unames = ['UserID', 'MovieID', 'rating', 'data']
data = pd.read_table('ratings.dat', sep='::', header=None, names=unames, engine='python')
# 6040
data['UserID'] -= 1
# 3952
data['MovieID'] -= 1
train_set_size = 100000
test_set_size = 20000
#
train_set = sp.coo_matrix((data['rating'][0:train_set_size],
                           (data['MovieID'][0:train_set_size], data['UserID'][0:train_set_size])),
                          shape=(3952, 6040)).tocsr()

cosine_dis2 = cosine_similarity(train_set, train_set)

cosine_dis2_ = sp.coo_matrix(cosine_dis2).tocsr()
denominator = cosine_dis2_.sum(axis=1)
x = train_set.todense()
xm = np.ma.MaskedArray(x, mask=(x == 0))

ave_col = np.mean(xm, axis=0)
ave_row = np.mean(xm, axis=1)
ave_all = np.mean(xm)
bias_all = ((ave_row - ave_all).filled(0) + (ave_col - ave_all).filled(0) + ave_all)
numerator = np.dot(cosine_dis2, (xm - bias_all).filled(0))

count = 0
for i in range(test_set_size):
    row_index = int(data['MovieID'][i + train_set_size])
    col_index = int(data['UserID'][i + train_set_size])
    if denominator[row_index] != 0:
        pred_stars = bias_all[row_index, col_index] + numerator[row_index, col_index] / denominator[row_index]
    else:
        pred_stars = bias_all[row_index, col_index]
    if abs(pred_stars -data['rating'][i + train_set_size]) < 1:
        count += 1

print(count / test_set_size)
