#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
import math

from evaluation import *

data_path = os.path.abspath('.') + '/data/'


def split_data(data, M, k, seed):
    train = []
    test = []
    random.seed(seed)
    for d in data:
        if random.randint(0, M) == k:
            test.append(d)
        else:
            train.append(d)
    return train, test


def make_matrix(users, N, C):
    """生成矩阵"""
    for u in users:
        if u not in N:
            N[u] = 1
        else:
            N[u] += 1
        if u not in C:
            C[u] = dict()
        for v in users:
            if u == v:
                continue
            if v not in C[u]:
                C[u][v] = 1
            else:
                C[u][v] += 1


def make_matrix1(users, N, C):
    """生成矩阵"""
    for u in users:
        if u not in N:
            N[u] = 1
        else:
            N[u] += 1
        if u not in C:
            C[u] = dict()
        for v in users:
            if u == v:
                continue
            if v not in C[u]:
                C[u][v] = 1
            else:
                C[u][v] += 1 / math.log(1 + len(users))


def user_similarity(train):
    """计算用户相似度  利用余弦相似度"""
    # build inverse table for item_users
    st = time.time()
    item_users = dict()
    for data in train:
        user, item = data['user'], data['item']
        if item not in item_users:
            item_users[item] = set()
        item_users[item].add(user)

    item_users = {item: users for item, users in item_users.items() if len(item_users[user]) > 0}
    # calculate co-rated items between users
    C = dict()
    N = dict()
    for item, users in item_users.items():
        # TODO 待优化 ，多线程 ，并行计算
        make_matrix(users, N, C)

    # calculate final similarity matrix W  余弦相似度
    W = dict()
    for u, relate_users in C.items():
        if u not in W:
            W[u] = dict()
        for v, cuv in relate_users.items():
            W[u][v] = cuv / math.sqrt(N[u] * N[v]) * 1.0
    print '计算用户相似度耗时，{%fs}' % (time.time() - st)
    return W


def user_similarity_advanced(train):
    """计算用户相似度改进版
            1
      —————————————     通过该式惩罚了用户u与用户v共同兴趣列表中热门物品对他们相似度的影响
      log1 + |N(i)|
    """
    # build inverse table for item_users
    st = time.time()
    item_users = dict()
    for data in train:
        user, item = data['user'], data['item']
        if item not in item_users:
            item_users[item] = set()
        item_users[item].add(user)

    # calculate co-rated items between users
    item_users = {item: users for item, users in item_users.items() if len(item_users[user]) > 0}
    C = dict()
    N = dict()
    for item, users in item_users.items():
        # TODO 待优化 ，多线程 ，并行计算
        make_matrix1(users, N, C)

    # calculate final similarity matrix W  余弦相似度改进版
    W = dict()
    for u, relate_users in C.items():
        if u not in W:
            W[u] = dict()
        for v, cuv in relate_users.items():
            W[u][v] = cuv / math.sqrt(N[u] * N[v]) * 1.0
    print '计算用户相似度耗时，{%fs}' % (time.time() - st)
    return W


def recommend(user, train, W, top):
    """推荐"""
    rank = dict()
    interacted_items = [d['item'] for d in train[user]]

    related_users = sorted(W[user].iteritems(), key=lambda d: d[1], reverse=True)[0:top]
    for v, wuv in related_users:
        for ui in train[v]:
            i, rvi = ui['item'], ui['rating']
            if i in interacted_items:
                # we should filter items user interacted before
                continue
            if i not in rank:
                rank[i] = wuv * float(1)
            else:
                rank[i] += wuv * float(1)
    rank = sorted(rank.iteritems(), key=lambda d: d[1], reverse=True)[0:top]

    return rank


if __name__ == "__main__":
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    path = os.path.abspath('.') + '/data/ml-100k/u.data'
    lines = []
    file = open(path)
    lines = file.readlines()
    file.close()
    data = []
    for line in lines:
        line = line.replace('\n', '')
        meta_data = dict()
        values = line.split('\t')
        # noinspection PyBroadException
        try:
            meta_data['user'] = values[0]
            meta_data['item'] = values[1]
            meta_data['rating'] = values[2]
            meta_data['timestamp'] = values[3]
            data.append(meta_data)
        except:
            continue

    train, test = split_data(data, 8, 1, 4)
    # print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    # # w = user_similarity(train)
    # w = user_similarity_advanced(train)
    # print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    # st = time.time()
    # # file1 = open(os.path.abspath('.') + '/data/123.data', 'w')
    # # file1.write(repr(w))
    # # file1.close()
    # file1 = open(os.path.abspath('.') + '/data/1234.txt', 'w')
    # file1.write(json.dumps(w))
    # file1.close()
    # print '写入耗时，{%fs}' % (time.time() - st)
    st = time.time()
    train1 = dict()
    for data1 in train:
        user = data1['user']
        if user not in train1:
            train1[user] = [data1]
        else:
            train1[user].append(data1)
    test1 = dict()
    for data1 in test:
        user = data1['user']
        if user not in test1:
            test1[user] = [data1]
        else:
            test1[user].append(data1)
    print '整理数据耗时，{%fs}' % (time.time() - st)

    recall(train1, test1, 5, '1234.txt', recommend)
    precision(train1, test1, 5, '1234.txt', recommend)
    coverate(train1, test1, 5, '1234.txt', recommend)
    popularity(train1, test1, 5, '1234.txt', recommend)
