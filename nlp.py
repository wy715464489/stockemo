from datetime import datetime
from math import *
import jieba
import pandas as pd
import synonyms as sy
from numpy import *
import os

now = datetime.now()


def weight_freq(s, influ):
    word_freq = []
    allw = list(jieba.cut(s))
    for i in set(allw):
        word_freq.append((i, allw.count(i) * influ))
    return word_freq


def emotion_basic(fp, env):
    try:
        posts = pd.read_csv(fp)
    except:
        return
    count = []
    for i in range(posts.shape[0]):
        time_delta = (now - pd.to_datetime(posts['publish'][i])).days
        influ = env * posts['age'][i] * (0.9 + posts['reputation'][i] * 0.02) / exp(time_delta / 60)
        count += weight_freq(str(posts['normal'][i]), influ)
    return count


def emotion_advanced():
    article_title = pd.read_csv('./tmp/_title.csv')
    count = []
    for p in range(article_title.shape[0]):
        env = log((1 + article_title['reader'][p]) * (1 + article_title['remark'][p]))
        if article_title['em'][p] in ['公告', '资讯']:
            env *= 5
        try:
            count += emotion_basic('./tmp/posts/' + str(p) + '.csv', env)
        except TypeError:
            pass
    return count


def word_synonym(freq_tu):
    freq = {}
    for i in freq_tu:
        freq[i[0]] = i[1]
    freqwords = list(freq.keys())
    for k in freqwords:
        try:
            syno = list(sy.nearby(k)[0])
            syno_p = list(sy.nearby(k)[1])
            for i in range(1, len(syno)):
                if syno[i] in freq.keys():
                    freq[k] += syno_p[i] * freq[syno[i]]
                    del freq[syno[i]]
        except KeyError:
            pass
    try:
        del freq['nan']
    except KeyError:
        pass
    freq_tu = []
    for i, j in freq.items():
        freq_tu.append((i, j))
    return freq_tu


def word_freq(count):
    sp_word = list(set([k[0] for k in count]))
    freq = dict(zip(sp_word, [0] * len(sp_word)))
    for k in count:
        freq[k[0]] += k[1]
    with open('sync.txt') as f_obj:
        line = f_obj.read().split('\n')
        line.append('\n')
    for i in line:
        while i in freq.keys():
            del freq[i]
    freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    if len(freq) > 500:
        freq = freq[:500]
    freq = word_synonym(freq)
    freq = sorted(freq, key=lambda x: x[1], reverse=True)
    if len(freq) > 20:
        freq = freq[:20]
    highfreq = {}
    for i in freq:
        highfreq[i[0]] = i[1]
    return highfreq


def boson_load():
    (workdir, _) = os.path.split(__file__)
    boson_path = workdir + '/BosonNLP.txt'
    with open(boson_path, 'r', encoding='utf-8') as fobj:
        line = fobj.read().split('\n')
    boson = {}
    for x in line:
        try:
            boson[x.split(' ')[0]] = float(x.split(' ')[1])
        except IndexError or ValueError:
            pass
    return boson


def fix_emo(highfreq, boson):
    for i in highfreq.keys():
        emo = 0
        (x, w) = sy.nearby(i)
        for j in range(len(x)):
            if x[j] in boson.keys():
                emo += boson[x[j]] * w[j]
            else:
                w[j] = 0
        if sum(w) == 0:
            highfreq[i] = 0
        else:
            highfreq[i] = emo / sum(w)
    return highfreq
