import os
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup

session = requests.Session()
firefox = {
    'Host': 'guba.eastmoney.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Referer': '',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Cookie': 'st_pvi=23213776327651; st_si=02372924174755; qgqp_b_id=3a062958f3310c97bbbeb43d2e9ca6af; st_sn=1; '
              'st_psi=20181117154551965-113300300978-5665118681; st_asi=delete',
    'Upgrade-Insecure-Requests': '1',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
}


def get_title(code, page):
    """
    :param code: code of stock
    :param page: index of present page
    :return:
    """
    url = 'http://guba.eastmoney.com/list,' + str(code) + '_' + str(page) + '.html'
    firefox['Referer'] = 'http://guba.eastmoney.com/list,' + str(code) + '_2.html'
    req = session.get(url, headers=firefox)
    req.raise_for_status()
    req.encoding = req.apparent_encoding
    tree = BeautifulSoup(req.text, features='html.parser')
    tree = tree.find('div', {'id': 'articlelistnew'})
    article_entry = tree.find_all('div', {'class': 'articleh normal_post'})
    article_entry += tree.find_all('div', {'class': 'articleh normal_post odd'})
    article_title = {
        'reader': [], 'remark': [], 'title': [], 'url': [], 'em': [], 'author': [],
    }
    for i in article_entry:
        reader = i.find('span', {'class': 'l1'}).text
        remark = i.find('span', {'class': 'l2'}).text
        title = i.find('span', {'class': 'l3'}).a.text
        url = 'http://guba.eastmoney.com' + i.find('span', {'class': 'l3'}).a.get('href')
        try:
            em = i.find('span', {'class': 'l3'}).em.text
            em = re.sub('\s', '', em)
        except AttributeError:
            em = ''
        if '￥' in em:
            continue
        author = i.find('span', {'class': 'l4'}).text
        article_title['reader'].append(reader)
        article_title['remark'].append(remark)
        article_title['title'].append(title)
        article_title['url'].append(url)
        article_title['em'].append(em)
        article_title['author'].append(author)
    return article_title


def main(code, page):
    """
    :param code: code of the stock
    :param page: amount of pages that request
    :return: action /save info of all articles in _title.csv
    """
    try:
        os.mkdir('./tmp')
    except FileExistsError:
        pass
    article_title = {
        'reader': [], 'remark': [], 'title': [], 'url': [], 'em': [], 'author': [],
    }
    pd.DataFrame(article_title).to_csv('./tmp/_title.csv', header=True, index=False, mode='w')
    for i in range(page):
        article_title = get_title(code, i + 1)
        pd.DataFrame(article_title).to_csv('./tmp/_title.csv', header=False, index=False, mode='a+')
