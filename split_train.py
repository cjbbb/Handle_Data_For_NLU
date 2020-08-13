from random import random

import numpy as np

np.random.seed(3234764685)
SPLIT_RATE = .2
train = {}

with open('data/a_train.txt', 'r', encoding='utf-8') as fin:
    for line in fin:
        query = eval(line)
        if '+' in query['intent']:
            continue
        train.setdefault(query['intent'], [])
        train[query['intent']].append(query)

with open('data/a_train.txt', 'w', encoding='utf-8') as ftrain:
    with open('data/a_else.txt', 'w', encoding='utf-8') as felse:
        for kind in train:
            # kind == intent
            total = len(train[kind])
            top = int(SPLIT_RATE * total)
            id_list = [i for i in range(total)]
            np.random.shuffle(id_list)
            print(top)
            # 随机id_list
           # print(train[kind][0])

            for item in [train[kind][i] for i in id_list[:top]]:
                ftrain.write('%s\n' % str(item))
            for item in [train[kind][i] for i in id_list[top:]]:
                felse.write('%s\n' % str(item))
