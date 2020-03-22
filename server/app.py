#!/usr/bin/env python
#coding:utf-8
import numpy as np
import pickle
from urllib import parse
import traceback

word_dict=pickle.load(open('words_vector_after.txt', 'rb'),encoding="UTF-8")
# print('word_dict',word_dict)

# articles=pickle.load(open('./articles.txt', 'rb'))
# titles=pickle.load(open('./titles.txt', 'rb'))

import re
def token(string):
    return re.findall('\w+',string)

import jieba
def cut(string):
    return jieba.lcut(string)

word_frequency=pickle.load(open('word_frequency_after.txt', 'rb'))

import re

def split_sentences_2(text,filter_p='\s+'):
    f_p = re.compile(filter_p)
    sentences = re.split(r"([。!！?？；;，,])", text)#处理标点符号
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
        if(sen.count("\n")>=2):#在后续的句子全文相关度计算中，我们将小标题视为段首
            delimiter = '\n'
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
        if '\n'in sen:
            paragraph_head_list.append(sub_sentences.index(sen))
        sen=re.sub('\s+','',sen)
        sub_sentences_clean.append(sen)  
    
    sen_vec = embed_fn(text) #新闻全文向量
    title_vec = embed_fn(title) #标题向量
    
    corr_score = {} #字典储存每一句子的全文相关度
    if sub_sentences_clean[len(sub_sentences_clean)-1]=="":
        sub_sentences_clean.pop(len(sub_sentences_clean)-1)
        if(len(paragraph_head_list)>0):
            paragraph_head_list.pop(len(paragraph_head_list)-1)
    for sen in sub_sentences_clean:
        sub_sen_vec = embed_fn(sen)#句子向量
        corr_score[sen] = 0.3* cosine(sen_vec,sub_sen_vec)+ 0.7 *cosine(title_vec,sub_sen_vec)
        if(len(sen)<=4):#字数小于3的句子，我们认为是个连词；连词句子向量本来偏高，在摘要中重要性也不大，所以将连词的全文相关度降低
            corr_score[sen]=corr_score[sen]*0.75
#         print(sen,corr_score[sen],cosine(title_vec,sub_sen_vec),cosine(sen_vec,sub_sen_vec))
#     print("after knn")
    knn(sub_sentences_clean, corr_score, paragraph_head_list)
    return sorted(corr_score.items(),key=lambda x:x[1],reverse=True)

# get_corr(articles[1],titles[1])

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

title = '国务院常务会议提出抓紧出台普惠金融定向降准措施推动降低融资成本'
article='新华社北京3月11日电（记者张千千）日前召开的国务院常务会议提出，要抓紧出台普惠金融定向降准措施，并额外加大对股份制银行的降准力度，促进商业银行加大对小微企业、个体工商户贷款支持，帮助复工复产，推动降低融资成本。\n国家金融与发展实验室副主任曾刚表示，出台普惠金融定向降准措施能够为金融机构提供长期资金，降低资金成本，以达到支持实体经济，特别是支持小微企业、个体工商户的目的。\n中国民生银行首席研究员温彬认为，额外加大对股份制银行的降准力度，一方面是由于股份制银行的客户以中小微企业为主，在支持中小微企业方面具有独特优势；另一方面，股份制银行整体面临着负债压力较大、负债成本较高的问题，为股份行提供长期低成本资金有助于其优化负债结构、降低负债成本，更好发挥支持中小微企业的比较优势。\n中国人民银行日前召开电视电话会议指出，在前期已经设立3000亿元疫情防控专项再贷款的基础上，增加再贷款再贴现专用额度5000亿元，同时，下调支农、支小再贷款利率0.25个百分点至2.5%。\n曾刚表示，通过专项再贷款等政策，央行能够向金融机构提供低成本资金，支持金融机构对疫情防控物资保供、农业和企业特别是小微企业提供优惠利率的信贷支持，助力其应对疫情冲击，顺利实现复工复产。\n国务院常务会议提出，要进一步把政策落到位，加快贷款投放进度，更好保障防疫物资保供、春耕备耕、国际供应链产品生产、劳动密集型产业、中小微企业等资金需求。\n此外，会议还提出要有序推动全产业链加快复工复产，引导金融机构主动对接产业链核心企业，加大流动资金贷款支持，给予合理信用额度等。'
text = get_summarization_by_sen_emb(article,title,200)
print('text',text)

import web
import json

urls = (
    '/index', 'index'   
)

app = web.application(urls, globals())

class index:
    def GET(self):
        web.header("Access-Control-Allow-Origin", "*") # 解决跨域问题
        
    
        query = web.input()
        content = parse.unquote(query.content)
        title = parse.unquote(query.title)
        res = get_summarization_by_sen_emb(content, title, 200)
        return json.dumps({'code':1,"data":res}) # 解决乱码
        

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
