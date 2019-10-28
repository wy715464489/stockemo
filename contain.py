import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

session = requests.Session()
firefox_contain = {
    'Host': 'guba.eastmoney.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Referer': '',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Cookie': 'st_pvi=23213776327651; st_si=02372924174755; qgqp_b_id=f29db22e77c5be9d3b9091abe84a6209; st_sn=1; '
              'st_psi=20181117154551965-113300300978-5665118681; st_asi=delete; '
              'yzmkey=d8f35f568c654f2e8c0573a113baf25f',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
}
error_box = []


def age_deal(age):
    try:
        age = re.findall("[\d\.\d]*", age)[0]
        if '年' in age:
            try:
                age = float(age)
            except ValueError:
                age = 0
        elif '个月' in age:
            try:
                age = float(age) / 12
            except ValueError:
                age = 0
    except IndexError:
        age = 0
    return age


def get_contain(code, url, em=None):
    firefox_contain['Referer'] = 'http://guba.eastmoney.com/list,' + str(code) + '_1.html'
    try:
        req = session.get(url, headers=firefox_contain)
    except:
        error_box.append('No network connection: ' + url)
        return
    req.raise_for_status()
    req.encoding = req.apparent_encoding
    tree_all = BeautifulSoup(req.text, features='html.parser')
    posts = {
        'age': [], 'reputation': [], 'publish': [], 'normal': [],
    }
    """the main post"""
    tree = tree_all.find('div', {'id': 'zwcontent'})
    try:
        age = tree.find('div', {'id': 'zwconttbn'}).find('div', {'class': 'influence_wrap'}).get('data-user_age')
    except:
        age = None
    age = age_deal(age)
    reputation = tree.find('div', {'id': 'zwconttbn'}).find('div', {'class': 'influence_wrap'}).get('data-user_level')
    try:
        reputation = int(reputation)
    except ValueError:
        reputation = 0
    publish = tree.find('div', {'id': 'zwconttb'}).find('div', {'class': 'zwfbtime'}).text
    try:
        publish = datetime.strptime(publish[4:23], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        publish = datetime.strptime('2010-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    if em == '问董秘':
        normal = tree.find('div', {'class': 'zwcontentmain'}).find('div', {'class': 'content_wrap'}).div.text
        normal = re.sub('[^\u4e00-\u9fa5]+', '', normal)
    elif em == '资讯':
        normal = tree.find('div', {'id': 'zwconbody'}).find('div', {'id': 'zw_body'}).text
        normal = re.sub('[^\u4e00-\u9fa5]+', '', normal)
    elif em == '公告':
        normal = tree.find('div', {'id': 'post_content'}).text
        normal = re.sub('[^\u4e00-\u9fa5]+', '', normal)
    else:
        try:  # normal format
            normal = tree.find('div', {'id': 'zwconbody'}).find('div', {'class': 'stockcodec .xeditor'}).text
            normal = re.sub('[^\u4e00-\u9fa5]+', '', normal)
        except AttributeError:
            normal = ''
    posts['age'].append(age)
    posts['reputation'].append(reputation)
    posts['publish'].append(publish)
    posts['normal'].append(normal)
    """all comment"""
    tree = tree_all.find('div', {'id': 'zwlist'})
    try:
        cmtlist = tree.find_all('div', {'class': 'zwlitxt'})
    except TypeError:
        print('fail')
        return posts
    for p in cmtlist:
        age = p.find('div', {'class': 'influence_wrap'}).get('data-user_age')
        age = age_deal(age)
        reputation = p.find('div', {'class': 'influence_wrap'}).get('data-user_influ_level')
        try:
            reputation = int(reputation)
        except ValueError:
            reputation = 0
        publish = p.find('div', {'class': 'zwlitime'}).text
        try:
            publish = datetime.strptime(publish[4:23], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            publish = datetime.strptime('2010-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        try:
            normal = p.find('div', {'class': 'zwlitext stockcodec'}).div.text
            normal = re.sub('[^\u4e00-\u9fa5]+', '', normal)
        except AttributeError:
            normal = ''
        posts['age'].append(age)
        posts['reputation'].append(reputation)
        posts['publish'].append(publish)
        posts['normal'].append(normal)
    return posts
