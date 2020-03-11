import pickle

word_frequency={}
for line in (open('word_frequency.txt')):
    key = line.split()[0]
    value = line.split()[1]
    word_frequency[key] = value

print(word_frequency)
pickle.dump(word_frequency,open('word_frequency_after.txt','wb'))