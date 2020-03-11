import numpy as np
word_vector=np.load('words_vector.npy',allow_pickle= True)
word_dict = {}
for i in range(len(word_vector)):
    word_dict[word_vector[i][0]]=word_vector[i][1]
word_dict

# np.save('words_vector_after.npy',word_dict)
import pickle
pickle.dump(word_dict,open('words_vector_after.txt','wb'))


# 2
word_frequency={}
for line in (open('word_frequency.txt')):
    key = line.split()[0]
    value = line.split()[1]
    word_frequency[key] = value
# word_frequency

# np.save('word_frequency_after.npy',word_frequency)
pickle.dump(word_frequency,open('word_frequency_after.txt','wb'))

# 3
filename = 'sqlResult_1558435.csv'
import pandas as pd
content = pd.read_csv(filename, encoding='gb18030')
content.head()

articles = content['content'].tolist()
titles = content['title'].tolist()

