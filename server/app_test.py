# coding:utf-8
import numpy as np
word_vector = np.load('./words_vector.npy',allow_pickle= True)
word_dict = {}
for i in range(len(word_vector)):
    word_dict[word_vector[i][0]]=word_vector[i][1]
word_dict