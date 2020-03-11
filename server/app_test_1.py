# coding:utf-8
import numpy as np
import pickle
# word_vector = np.load('./words_vector.npy',allow_pickle= True)
# word_dict = {}
# for i in range(len(word_vector)):
#     word_dict[word_vector[i][0]]=word_vector[i][1]

word_dict=pickle.load(open('./words_vector_after.txt', 'rb'))



# articles=pickle.load(open('./articles.txt', 'rb'))
# titles=pickle.load(open('./titles.txt', 'rb'))


import re
def token(string):
    return re.findall('\w+',string)

import jieba
def cut(string):
    return jieba.lcut(string)



word_frequency=pickle.load(open('./word_frequency_after.txt', 'rb'))



import re

def split_sentences_2(text,filter_p='\s+'):
    f_p = re.compile(filter_p)
    text = re.sub(f_p,'',text) ## \r\n strip
    sentences = re.split(r"([。!！?？；;，,\s+])", text)
    sentences.append("")
    sentences = ["".join(i) for i in zip(sentences[0::2],sentences[1::2])]
    return sentences


# from sklearn.decomposition import PCA
def cut2(text): return ' '.join(jieba.cut(text))


def SIF_sentence_embedding(text, alpha=1e-4):
    global word_frequency

    max_fre = max(word_frequency.values()).any()
    sen_vec = np.zeros_like(word_dict['的'])
    words = cut2(text).split()
    words = [w for w in words if w in word_dict]
    #     print(words)
    for w in words:
        #         print(w)
        #         print(word_frequency[w])
        fre = word_frequency.get(w, max_fre)
        weight = alpha / (float(fre) + alpha)
        sen_vec += weight * word_dict[w]

    sen_vec /= len(words)
    # pca
    #     pca = PCA(svd_solver='full')
    #     sen_vec_pac = pca.fit(sen_vec.reshape(-1,1))
    return sen_vec


from scipy.spatial.distance import cosine


def knn(sub_sentences, score):
    for i in range(len(sub_sentences)):
        if i == 0:
            score[sub_sentences[i]] = 0.2 * score[sub_sentences[i + 1]] + 0.3 + 0.5 * score[sub_sentences[i]]
        elif i == len(sub_sentences) - 1:
            score[sub_sentences[i]] = 0.3 * score[sub_sentences[i - 1]] + 0.2 + 0.5 * score[sub_sentences[i]]
        else:
            score[sub_sentences[i]] = 0.3 * score[sub_sentences[i + 1]] + 0.2 * score[sub_sentences[i - 1]] + 0.5 * \
                                      score[sub_sentences[i]]
        print(sub_sentences[i], score[sub_sentences[i]])

    return score


def get_corr(text, title, embed_fn=SIF_sentence_embedding):
    if isinstance(text, list): text = ' '.join(text)

    sub_sentences = split_sentences_2(text)
    sen_vec = embed_fn(text)
    title_vec = embed_fn(title)

    corr_score = {}
    sub_sentences_clean = []
    for sen in sub_sentences:
        if sen == "":
            continue
        sub_sentences_clean.append(sen)
        sub_sen_vec = embed_fn(sen)
        corr_score[sen] = 0.3 * cosine(sen_vec, sub_sen_vec) + 0.7 * cosine(title_vec, sub_sen_vec)
        print(sen, corr_score[sen], cosine(title_vec, sub_sen_vec), cosine(sen_vec, sub_sen_vec))
    print("after knn")
    knn(sub_sentences_clean, corr_score)
    return sorted(corr_score.items(), key=lambda x: x[1], reverse=True)





def get_summarization(text, title, score_fn, sum_len):
    #     sum_len = len(text)/2
    sub_sentences = split_sentences_2(text)
    ranking_sentences = score_fn(text, title)
    selected_sen = set()
    current_sen = ''

    for sen, _ in ranking_sentences:
        if len(current_sen) < sum_len:
            current_sen += sen
            selected_sen.add(sen)
        else:
            break

    summarized = []
    for sen in sub_sentences:
        if sen in selected_sen:
            summarized.append(sen)
    return summarized


def get_summarization_by_sen_emb(text, title, max_len):
    sens = get_summarization(text, title, get_corr, max_len)
    return ''.join(sens)



import web
import json

urls = (
    '/index', 'index'   
)

app = web.application(urls, globals())
