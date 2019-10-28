import os
import sys

import pandas as pd
import requests
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class MyWindow(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()
        """ Main Window """
        self.setFont(QFont("宋体", 10.5))
        window_pale = QPalette()
        self.setPalette(window_pale)
        self.resize(600, 400)
        self.center()
        self.setWindowTitle('证券A股的投资者舆情情感分析软件')
        """ Variable """
        self.code = None
        self.page = None
        """ Search Label """
        self.label1 = QLabel(self)
        self.label1.setText("股票代码：")
        self.label1.resize(60, 20)
        self.label1.move(10, 20)
        self.label1.setStyleSheet("color:black")
        """ Search Input Box """
        self.box1 = QLineEdit(self)
        self.box1.resize(100, 20)
        self.box1.move(70, 20)
        """ Hometown Label """
        self.label2 = QLabel(self)
        self.label2.setText("查询页数：")
        self.label2.resize(60, 20)
        self.label2.move(180, 20)
        self.label2.setStyleSheet("color:black")
        """ Hometown Input Box """
        self.box2 = QLineEdit(self)
        self.box2.resize(60, 20)
        self.box2.move(245, 20)
        """ Run Button """
        self.button1 = QPushButton('分析', self)
        self.button1.resize(50, 20)
        self.button1.move(320, 20)
        self.button1.clicked.connect(self.signal1)
        """ Draw Button """
        self.button1 = QPushButton('绘图', self)
        self.button1.resize(50, 20)
        self.button1.move(380, 20)
        self.button1.clicked.connect(self.signal2)
        """ Main Text Book """
        self.box4 = QTextBrowser(self)
        self.box4.append("可查询扩展市场行情：guba.eastmoney.com/list,<code>.html")
        self.box4.append("<code>为东方财富股吧号，如美元人民币中间价：usdcnyc")
        self.box4.append("在别人贪婪时恐惧，在别人恐惧时贪婪。——巴菲特")
        self.box4.resize(540, 300)
        self.box4.move(30, 60)
        self.show()

    def signal1(self):
        self.box4.clear()
        self.code = self.box1.text()
        try:
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
                'Cookie': 'st_pvi=23213776327651; st_si=02372924174755; qgqp_b_id=3a062958f3310c97bbbeb43d2e9ca6af; '
                          'st_sn=1; st_psi=20181117154551965-113300300978-5665118681; st_asi=delete',
                'Upgrade-Insecure-Requests': '1',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache',
            }
            url = 'http://guba.eastmoney.com/list,' + str(self.code) + '_1.html'
            firefox['Referer'] = 'http://guba.eastmoney.com/list,' + str(self.code) + '_2.html'
            _ = session.get(url, headers=firefox)
        except:
            self.box4.append("网络连接错误。")
            self.code = None
        try:
            self.page = abs(int(self.box2.text()))
        except ValueError:
            self.box4.append("股票代码、查询页数应为正整数。")
            self.page = None
        if self.code and self.page:
            self.branch_line = Thread(self.code, self.page)
            self.branch_line.start()
            self.branch_line.signal.connect(self.update)
            self.branch_line.wordart.connect(self.draw)
            self.branch_line.wordart2.connect(self.draw2)
        else:
            self.box4.append("分析失败。")

    def signal2(self):
        import figure
        try:
            figure.main(self.wordart, self.wordart2)
        except AttributeError:
            self.box4.clear()
            self.box4.append("无运行结果。")

    def draw(self, msg):
        self.wordart = msg

    def draw2(self, msg):
        self.wordart2 = msg

    def update(self, msg):
        self.box4.append(msg)

    def center(self):
        fg = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        fg.moveCenter(cp)
        self.move(fg.topLeft())


class Thread(QThread):
    signal = pyqtSignal(str)
    wordart = pyqtSignal(dict)
    wordart2 = pyqtSignal(dict)

    def __init__(self, code, page, parent=None):
        super().__init__(parent)
        self.code = code
        self.page = page

    def run(self):
        import collect
        try:
            collect.main(self.code, self.page)
        except:
            self.signal.emit("论坛帖目录收集错误。")
            return self.signal.emit("分析失败。")
        self.signal.emit("论坛帖目录收集完成。(1/5)")
        import contain
        try:
            os.mkdir('./tmp/posts')
        except FileExistsError:
            pass
        article_title = pd.read_csv('./tmp/_title.csv')
        for o in range(article_title.shape[0]):
            posts = contain.get_contain(self.code, article_title['url'][o], article_title['em'][o])
            pd.DataFrame(posts).to_csv('./tmp/posts/' + str(o) + '.csv', index=False)
            self.signal.emit("论坛帖获取进度：" + str(o + 1) + "/" + str(article_title.shape[0]))
        self.signal.emit("论坛帖收集完成。(2/5)")
        import nlp
        from numpy import average
        self.signal.emit("NLP模块加载完成。(3/5)")
        count = nlp.emotion_advanced()
        highfreq = nlp.word_freq(count)
        self.wordart.emit(highfreq)
        self.signal.emit("高频词统计完成。(4/5)")
        highfreq = dict(zip(highfreq.keys(), [0] * len(highfreq.keys())))
        boson = nlp.boson_load()
        highfreq = nlp.fix_emo(highfreq, boson)

        self.wordart2.emit(highfreq)
        emt = average(list(highfreq.values()))
        self.signal.emit("情感比对统计完成。(5/5)")
        self.signal.emit("平均情感积极性：" + str(emt))
        if emt >= 6:
            self.signal.emit("数据显示：投资者对这个股票非常乐观。")
        elif 4 <= emt < 6:
            self.signal.emit("数据显示：投资者对这个股票持乐观态度。")
        elif 2 <= emt < 4:
            self.signal.emit("数据显示：投资者对这个股票比较乐观。")
        elif 0.5 <= emt < 2:
            self.signal.emit("数据显示：投资者对这个股票中立偏积极。")
        elif -0.5 < emt < 0.5:
            self.signal.emit("数据显示：投资者对这个股票持中立态度。")
        elif -2 < emt <= -0.5:
            self.signal.emit("数据显示：投资者对这个股票中立偏消极。")
        elif -4 < emt <= -2:
            self.signal.emit("数据显示：投资者对这个股票比较消极。")
        elif -6 < emt <= -4:
            self.signal.emit("数据显示：投资者对这个股票持消极态度。")
        elif emt <= -6:
            self.signal.emit("数据显示：投资者对这个股票非常消极。")
        else:
            self.signal.emit("未得出结果。")
        self.signal.emit("高频词：" + " ".join(list(highfreq.keys())))
        return self.signal.emit("分析结束。")


app = QApplication(sys.argv)
myw = MyWindow()
myw.show()
sys.exit(app.exec_())
