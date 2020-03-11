import pickle
import pandas as pd

filename = 'sqlResult_1558435.csv'
content = pd.read_csv(filename, encoding='gb18030')
content.head()
articles = content['content'].tolist()
titles = content['title'].tolist()


pickle.dump(articles,open('articles.txt','wb'))
pickle.dump(titles,open('titles.txt','wb'))

# word_frequency={}
# for line in (open('word_frequency.txt')):
#     key = line.split()[0]
#     value = line.split()[1]
#     word_frequency[key] = value

# print(word_frequency)
# pickle.dump(word_frequency,open('word_frequency_after.txt','wb'))