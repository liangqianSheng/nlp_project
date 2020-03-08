# coding:utf-8
import numpy as np
word_vector = np.load('./words_vector.npy',allow_pickle= True)
word_dict = {}
for i in range(len(word_vector)):
    word_dict[word_vector[i][0]]=word_vector[i][1]
word_dict


filename = 'sqlResult_1558435.csv'
import pandas as pd
# content = pd.read_csv(filename, encoding='gb18030')
# content.head()

# articles = content['content'].tolist()
# titles = content['title'].tolist()
import re
def token(string):
    return re.findall('\w+',string)

import jieba
def cut(string):
    return jieba.lcut(string)

# word_frequency={}
# for line in (open('word_frequency.txt')):
#     key = line.split()[0]
#     value = line.split()[1]
#     word_frequency[key] = value
# word_frequency

# print('word_frequency',word_frequency)
