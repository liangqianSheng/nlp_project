#!/usr/bin/env python
import numpy as np
import pickle
from urllib import parse
import traceback


word_dict=pickle.load(open('./words_vector_after.txt', 'rb'),encoding="UTF-8")
# print('word_dict',word_dict)



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
    sentences = re.split(r"([。!！?？；;，,\\])", text)#处理标点符号
    revised_sentences=[]
    for sen in sentences:
        #处理特殊标点符号
        if ('“' in sen)and('”' in sen):#保留成对的引号
            revised_sentences.append(sen)
        elif ('(' in sen)and(')' in sen)or('{' in sen)and('}' in sen)or('[' in sen)and(']' in sen)or('（' in sen)and('）' in sen):
            sen = re.sub('|’|‘|”|“|\'','',sen)## 去除单独的引号
            sen=re.sub(u"\\(.*?\\)|\\{.*?}|\\[.*?]|\\（.*?）", "", sen)#去掉括号以及括号内文字，因为在摘要中并不是很重要
            revised_sentences.append(sen)
        else:
            sen = re.sub('|’|‘|”|“|\'|（|）','',sen)## 去除单独的引号、括号，以免影响句子完整性
            revised_sentences.append(sen)
            
    revised_sentences_2=[]
    #为不以标定符号结尾的小标题添加句号，保证摘要生成的语句连贯；解释：出现2个以上\r\n时，最后一句以外的句子为小标题，最后一句为自然段段首
    for sen in revised_sentences:       
        if(sen.count("\r\n")>=2):#在后续的句子全文相关度计算中，我们将小标题视为段首
            delimiter = '\r\n'
            sen_pieces = [delimiter+k for k in sen.split(delimiter)]
            sen_pieces=sen_pieces[1:]
            for subtitle in sen_pieces[:-1]:
                revised_sentences_2.append(subtitle)
                revised_sentences_2.append("。")
            revised_sentences_2.append(sen_pieces[-1])
            continue
        revised_sentences_2.append(sen)

    revised_sentences_2.append("")
    revised_sentences_2 = ["".join(i) for i in zip(revised_sentences_2[0::2],revised_sentences_2[1::2])]
    return revised_sentences_2

# print(split_sentences_2(articles[110]))


# from sklearn.decomposition import PCA
def cut2(text): return ' '.join(jieba.cut(text)) 
def SIF_sentence_embedding(text,alpha=1e-4):
    global word_frequency
    
    max_fre = max(word_frequency.values())
    sen_vec = np.zeros_like(word_dict['的'])
    words = cut2(text).split()
    words = [w for w in words if w in word_dict]
#     print(words)
    for w in words:
#         print(w)
#         print(word_frequency[w])
        fre = word_frequency.get(w,max_fre)
        weight = alpha/(float(fre)+alpha)
        sen_vec += weight*word_dict[w]
        
    sen_vec /= len(words)
    #pca
#     pca = PCA(svd_solver='full')
#     sen_vec_pac = pca.fit(sen_vec.reshape(-1,1))
    return sen_vec


from scipy.spatial.distance import cosine

def knn(sub_sentences,score,paragraph_head_list):
    # print('sub_sentences',len(sub_sentences),len(paragraph_head_list),sub_sentences)
    for i in paragraph_head_list:#段首全文相关度权重比为0.25/0.25/0.5
        score[sub_sentences[i]] = 0.55 * score[sub_sentences[i+1]]+ 0.25 + 0.2 * score[sub_sentences[i]]
    
    for i in list(set(list(range(len(sub_sentences)))) - set(paragraph_head_list)):
        if i == 0:
            score[sub_sentences[i]] = 0.7 * score[sub_sentences[i+1]]+ 0.1 + 0.2 * score[sub_sentences[i]]
        elif i == len(sub_sentences)-1:
            score[sub_sentences[i]] = 0.3 * score[sub_sentences[i-1]]+0.2 + 0.5 * score[sub_sentences[i]]
        else:
            score[sub_sentences[i]] = 0.45* score[sub_sentences[i+1]]+ 0.35 * score[sub_sentences[i-1]]+ 0.2 * score[sub_sentences[i]]
#         print(sub_sentences[i],score[sub_sentences[i]])  
    return score
    
def get_corr(text,title,embed_fn=SIF_sentence_embedding):
    if isinstance(text,list): text = ' '.join(text)
    paragraph_head_list=[] #储存新一个自然段在第几句话出现
    sub_sentences_clean=[] #储存处理过“\r\n”的句子集合
    sub_sentences = split_sentences_2(text) #所有句子集合
    
    for sen in sub_sentences:
        if '\r\n'in sen:
            paragraph_head_list.append(sub_sentences.index(sen))
        sen=re.sub('\s+','',sen)
        sub_sentences_clean.append(sen)  
    
    sen_vec = embed_fn(text) #新闻全文向量
    title_vec = embed_fn(title) #标题向量
    
    corr_score = {} #字典储存每一句子的全文相关度
    if sub_sentences_clean[len(sub_sentences_clean)-1]=="":
        sub_sentences_clean.pop(len(sub_sentences_clean)-1)
        paragraph_head_list.pop(len(paragraph_head_list)-1)
    for sen in sub_sentences_clean:
#         if sen == "":
#             continue
        sub_sen_vec = embed_fn(sen)#句子向量
        corr_score[sen] = 0.3* cosine(sen_vec,sub_sen_vec)+ 0.7 *cosine(title_vec,sub_sen_vec)
        if(len(sen)<=4):#字数小于3的句子，我们认为是个连词；连词句子向量本来偏高，在摘要中重要性也不大，所以将连词的全文相关度降低
            corr_score[sen]=corr_score[sen]*0.75
#         print(sen,corr_score[sen],cosine(title_vec,sub_sen_vec),cosine(sen_vec,sub_sen_vec))
#     print("after knn")
    knn(sub_sentences_clean, corr_score, paragraph_head_list)
    return sorted(corr_score.items(),key=lambda x:x[1],reverse=True)

# get_corr(articles[1],titles[1])

import matplotlib.pyplot as plt
def analyse_knn_smooth(text,title,embed_fn=SIF_sentence_embedding):
    if isinstance(text,list): text = ' '.join(text)
    
    paragraph_head_list=[]
    sub_sentences_clean=[]
    sub_sentences = split_sentences_2(text) #所有句子集合
#     print(sub_sentences)
    
    for sen in sub_sentences:
        if '\r\n'in sen:
            paragraph_head_list.append(sub_sentences.index(sen))
        sen=re.sub('\s+','',sen)
        sub_sentences_clean.append(sen)  
    
    sen_vec = embed_fn(text) #新闻全文向量
    title_vec = embed_fn(title) #标题向量
    
    if sub_sentences_clean[len(sub_sentences_clean)-1]=="":
        sub_sentences_clean.pop(len(sub_sentences_clean)-1)
        paragraph_head_list.pop(len(paragraph_head_list)-1)
    
    corr_score = {} 
    for sen in sub_sentences_clean:
#         if sen == "":
#             sub_sentences_clean.remove(sen)
#             continue
        sub_sen_vec = embed_fn(sen)#句子向量
        corr_score[sen] = 0.3* cosine(sen_vec,sub_sen_vec)+ 0.7 *cosine(title_vec,sub_sen_vec)
#         print(sen,corr_score[sen],cosine(title_vec,sub_sen_vec),cosine(sen_vec,sub_sen_vec))

    for head_index in paragraph_head_list:#段首
        corr_score[sub_sentences_clean[head_index]] = 0.55 * corr_score[sub_sentences_clean[head_index+1]]+0.25 + 0.5 * corr_score[sub_sentences_clean[head_index]]

    for i in list(set(list(range(len(sub_sentences_clean)))) - set(paragraph_head_list)):
        if i == 0:#总起句
            corr_score[sub_sentences_clean[i]] = 0.7 * corr_score[sub_sentences_clean[i+1]]+ 0.1 + 0.2 * corr_score[sub_sentences_clean[i]]
        elif i == len(sub_sentences_clean)-1:#结尾句
            corr_score[sub_sentences_clean[i]] = 0.35 * corr_score[sub_sentences_clean[i-1]]+ 0.2+ 0.45 * corr_score[sub_sentences_clean[i]]
        else:#普通句
            corr_score[sub_sentences_clean[i]] = 0.45* corr_score[sub_sentences_clean[i+1]]+ 0.35 * corr_score[sub_sentences_clean[i-1]]+ 0.2 * corr_score[sub_sentences_clean[i]]
#         print(i,corr_score[sub_sentences_clean[i]])   
    # print(sorted(corr_score.items(),key=lambda x:x[1],reverse=True))  
    
    sentences_set=(corr_score).values()
    length_sentence=len(sentences_set)
    sentences=[] #储存原文句子的出现顺序
    for i in range(length_sentence):
        sentences.append(i+1)
    semantic_relevances=list(sentences_set)# 储存全文句子相关度
    
    arr_std = np.std(semantic_relevances,ddof=1)#求全文句子相关度的标准差
    print("标准差为 "+str(arr_std))
    
    fig, ax = plt.subplots()#做图
    ax.plot(sentences, semantic_relevances, label='Semantic relevance')
    plt.xlabel('K-th sentence in the article')
    plt.ylabel('Score')
    plt.title('KNN Smoothing Analysis')
    ax.legend()





def get_summarization(text,title,score_fn,sum_len):
  #     sum_len = len(text)/2
    sub_sentences = split_sentences_2(text)
    ranking_sentences = score_fn(text,title)
    selected_sen = set()
    current_sen = ''
    
    sub_sentences_clean=[]
    for sen in sub_sentences:
        sen=re.sub('\s+','',sen)
        sub_sentences_clean.append(sen)
        
    for sen, _ in ranking_sentences:
        if len(current_sen)<sum_len:
            current_sen += sen
            selected_sen.add(sen)
        else:
            break
                    
    summarized = []
    for sen in sub_sentences_clean:
        if sen in selected_sen:
            summarized.append(sen)
    return summarized

def get_summarization_by_sen_emb(text,title,max_len):
    sens = get_summarization(text,title,get_corr,max_len)
    return ''.join(sens)  

# print('origin',articles[5632])
# text = get_summarization_by_sen_emb(articles[5632],titles[5632],1100)


import web
import json

urls = (
    '/index', 'index'   
)

app = web.application(urls, globals())

class index:
    def GET(self):
        web.header("Access-Control-Allow-Origin", "*") # 解决跨域问题
        
        try:
            query = web.input()
            content = parse.unquote(query.content)
            title = parse.unquote(query.title)
            res = get_summarization_by_sen_emb(content, title, 200)
            # print('res',res);
            return json.dumps({'code':1,"data":res}) # 解决乱码
        except MemoryError:
            print('error:MemoryError',e)
            return json.dumps({'code':0,"message":'内存溢出错误'})
        except RuntimeError as e:
            print('error:RuntimeError',e)
            return json.dumps({'code':0,"message":'系统运行时错误'})
        except BaseException as e:
            print('error:BaseException',e)
            return json.dumps({'code':0,"message":'系统错误-1'})
        except Exception as e:
            print('error:Exception',e)
            return json.dumps({'code':0,"message":'系统错误-2'})
        else:
            return json.dumps({'code':0,"message":'系统错误-3'})

    def POST(self):
        print('post')
        web.header("Access-Control-Allow-Origin", "*")
        web.header('Access-Control-Allow-Credentials', ' true');
        web.header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS');
        
        web.header('Access-Control-Allow-Headers',
                   'Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization');

        data = web.input()
        return data


if __name__ == "__main__":
    app.run()