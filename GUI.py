from PyQt5 import QtCore, QtGui, QtWidgets
from datetime import date
from spider import *
from pythainlp import word_tokenize as token_th
from pythainlp.corpus import thai_stopwords

class TweetWorker(QtCore.QThread):
    running = False
    def __init__(self, keyword,startday,endday,tw_crawler):
        QtCore.QThread.__init__(self)
        self.keyword , self.start_day, self.end_day = keyword , startday , endday
        self.tw_crawler = tw_crawler

    def run(self):
        TweetWorker.running = True
        self.tw_crawler.search_tweets(self.keyword,self.start_day,self.end_day)
        TweetWorker.running = False

class WebWorker_Scrap(QtCore.QThread):
    def __init__(self,web_crawler):
        QtCore.QThread.__init__(self)
        self.web_crawler = web_crawler

    def run(self):
        self.web_crawler.default_scrap()

class WebWorker_Search(QtCore.QThread):
    finished = QtCore.pyqtSignal()
    def __init__(self,keyword,web_crawler):
        QtCore.QThread.__init__(self)
        self.keyword = keyword
        self.web_crawler = web_crawler

    def run(self):
        self.data = self.web_crawler.search_web(self.keyword)
        self.finished.emit()

class Ui_EZ_Scrap(object):
    def setupUi(self, EZ_Scrap):

        self.tw_crawler = TwitterCrawler()
        self.web_crawler = WebCrawler()

        self.qTimer = QtCore.QTimer()
        self.qTimer.setInterval(500)
        self.qTimer.timeout.connect(self.update_status)
        font = QtGui.QFont()
        font.setPointSize(14)
        EZ_Scrap.setObjectName("EZ_Scrap")
        EZ_Scrap.resize(1295, 760)
        self.centralwidget = QtWidgets.QWidget(EZ_Scrap)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 1281, 761))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.search_label = QtWidgets.QLabel(self.tab)
        self.search_label.setGeometry(QtCore.QRect(350, 10, 101, 41))
        self.search_label.setFont(font)
        self.search_label.setObjectName("search_label")
        self.export_bt = QtWidgets.QPushButton(self.tab)
        self.export_bt.setGeometry(QtCore.QRect(1100, 80, 151, 51))
        self.export_bt.setFont(font)
        self.export_bt.setObjectName("export_bt")
        self.export_bt.clicked.connect(self.export_file_tweet)
        self.lineEdit = QtWidgets.QLineEdit(self.tab)
        self.lineEdit.setGeometry(QtCore.QRect(470, 20, 651, 20))
        self.lineEdit.setObjectName("lineEdit")
        self.search_bt = QtWidgets.QPushButton(self.tab)
        self.search_bt.setGeometry(QtCore.QRect(1140, 10, 81, 41))
        self.search_bt.setFont(font)
        self.search_bt.setObjectName("search_bt")
        self.search_bt.clicked.connect(self.search_tweet)
        self.start_date = QtWidgets.QDateEdit(self.tab)
        self.start_date.setGeometry(QtCore.QRect(180, 10, 110, 22))
        self.start_date.setObjectName("start_date")
        self.start_date.setDate(date.today())
        self.start_date.setDisplayFormat("dd/MM/yyyy")
        self.end_date = QtWidgets.QDateEdit(self.tab)
        self.end_date.setGeometry(QtCore.QRect(180, 50, 110, 22))
        self.end_date.setObjectName("end_date")
        self.end_date.setDate(date.today() - timedelta(days=7))
        self.end_date.setDisplayFormat("dd/MM/yyyy")
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setGeometry(QtCore.QRect(30, 10, 121, 31))
        self.label.setFont(font)
        self.label_2 = QtWidgets.QLabel(self.tab)
        self.label_2.setGeometry(QtCore.QRect(30, 50, 121, 31))
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.listWidget = QtWidgets.QListWidget(self.tab)
        self.listWidget.setGeometry(QtCore.QRect(10, 310, 201, 301))
        self.listWidget.setObjectName("listWidget")
        self.listWidget.itemDoubleClicked.connect(self.showItem)
        self.label_3 = QtWidgets.QLabel(self.tab)
        self.label_3.setGeometry(QtCore.QRect(10, 240, 161, 41))
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.tab)
        self.label_4.setGeometry(QtCore.QRect(470, 50, 651, 41))
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.tabWidget.addTab(self.tab, "")
        self.tabWidget_2 = QtWidgets.QTabWidget(self.tab)
        self.tabWidget_2.setGeometry(QtCore.QRect(220, 120, 1081, 601))
        self.tabWidget_2.setObjectName("tabWidget_2")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.table = QtWidgets.QTableWidget(self.tab_3)
        self.table.setGeometry(QtCore.QRect(0, 0, 1051, 561))
        self.table.setObjectName("tableView")
        self.tabWidget_2.addTab(self.tab_3, "")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.positive_label = QtWidgets.QLabel(self.tab_4)
        self.positive_label.setGeometry(QtCore.QRect(10, 70, 231, 91))
        self.positive_label.setFont(font)
        self.positive_label.setObjectName("positive_label")
        self.neutral_label = QtWidgets.QLabel(self.tab_4)
        self.neutral_label.setGeometry(QtCore.QRect(360, 70, 231, 91))
        self.neutral_label.setFont(font)
        self.neutral_label.setObjectName("neutral_label")
        self.negative_label = QtWidgets.QLabel(self.tab_4)
        self.negative_label.setGeometry(QtCore.QRect(750, 70, 231, 91))
        self.negative_label.setFont(font)
        self.negative_label.setObjectName("negative_label")
        self.label_8 = QtWidgets.QLabel(self.tab_4)
        self.label_8.setGeometry(QtCore.QRect(20, 130, 221, 101))
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(self.tab_4)
        self.label_9.setGeometry(QtCore.QRect(370, 140, 221, 101))
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(self.tab_4)
        self.label_10.setGeometry(QtCore.QRect(770, 150, 221, 101))
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.related_label = QtWidgets.QLabel(self.tab_4)
        self.related_label.setGeometry(QtCore.QRect(10, 210, 231, 91))
        self.related_label.setFont(font)
        self.related_label.setObjectName("related_label")
        self.related_table = QtWidgets.QTableWidget(self.tab_4)
        self.related_table.setGeometry(QtCore.QRect(10, 280, 1041, 281))
        self.related_table.setObjectName("related_table")
        self.sentiment_label = QtWidgets.QLabel(self.tab_4)
        self.sentiment_label.setGeometry(QtCore.QRect(10, -10, 231, 91))
        self.sentiment_label.setFont(font)
        self.sentiment_label.setObjectName("sentiment_label")
        self.tabWidget_2.addTab(self.tab_4, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget_3 = QtWidgets.QTabWidget(self.tab_2)
        self.tabWidget_3.setGeometry(QtCore.QRect(10, 120, 1281, 601))
        self.tabWidget_3.setObjectName("tabWidget_3")
        self.tab_5 = QtWidgets.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.tabWidget_3.addTab(self.tab_5, "")
        self.tab_6 = QtWidgets.QWidget()
        self.tab_6.setObjectName("tab_6")
        self.positive_label_2 = QtWidgets.QLabel(self.tab_6)
        self.positive_label_2.setGeometry(QtCore.QRect(10, 70, 231, 91))
        self.positive_label_2.setFont(font)
        self.positive_label_2.setObjectName("positive_label_2")
        self.neutral_label_2 = QtWidgets.QLabel(self.tab_6)
        self.neutral_label_2.setGeometry(QtCore.QRect(360, 70, 231, 91))
        self.neutral_label_2.setFont(font)
        self.neutral_label_2.setObjectName("neutral_label_2")
        self.negative_label_2 = QtWidgets.QLabel(self.tab_6)
        self.negative_label_2.setGeometry(QtCore.QRect(750, 70, 231, 91))
        self.negative_label_2.setFont(font)
        self.negative_label_2.setObjectName("negative_label_2")
        self.label_11 = QtWidgets.QLabel(self.tab_6)
        self.label_11.setGeometry(QtCore.QRect(20, 130, 221, 101))
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.label_12 = QtWidgets.QLabel(self.tab_6)
        self.label_12.setGeometry(QtCore.QRect(370, 140, 221, 101))
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        self.label_13 = QtWidgets.QLabel(self.tab_6)
        self.label_13.setGeometry(QtCore.QRect(770, 150, 221, 101))
        self.label_13.setFont(font)
        self.label_13.setObjectName("label_13")
        self.related_label_2 = QtWidgets.QLabel(self.tab_6)
        self.related_label_2.setGeometry(QtCore.QRect(10, 210, 231, 91))
        self.related_label_2.setFont(font)
        self.related_label_2.setObjectName("related_label_2")
        self.related_table_2 = QtWidgets.QTableWidget(self.tab_6)
        self.related_table_2.setGeometry(QtCore.QRect(10, 280, 1041, 281))
        self.related_table_2.setObjectName("tableView_5")
        self.sentiment_label2 = QtWidgets.QLabel(self.tab_6)
        self.sentiment_label2.setGeometry(QtCore.QRect(10, -10, 231, 91))
        self.sentiment_label2.setFont(font)
        self.sentiment_label2.setObjectName("sentiment_label2")
        self.table_2 = QtWidgets.QTableWidget(self.tab_5)
        self.table_2.setGeometry(QtCore.QRect(0, 0, 1251, 571))
        self.table_2.setObjectName("tableView_2")
        self.label_5 = QtWidgets.QLabel(self.tab_2)
        self.label_5.setGeometry(QtCore.QRect(470, 50, 651, 41))
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.tab_2)
        self.lineEdit_2.setGeometry(QtCore.QRect(480, 10, 651, 31))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.search_bt_2 = QtWidgets.QPushButton(self.tab_2)
        self.search_bt_2.setGeometry(QtCore.QRect(1160, 0, 81, 51))
        self.search_bt_2.setFont(font)
        self.search_bt_2.setObjectName("search_bt_2")
        self.search_bt_2.clicked.connect(self.search_web)
        self.scrap_bt = QtWidgets.QPushButton(self.tab_2)
        self.scrap_bt.setGeometry(QtCore.QRect(280, 0, 81, 51))
        self.scrap_bt.setFont(font)
        self.scrap_bt.setObjectName("scrap_bt")
        self.scrap_bt.clicked.connect(self.scrap)
        self.export_bt_2 = QtWidgets.QPushButton(self.tab_2)
        self.export_bt_2.setGeometry(QtCore.QRect(1120, 60, 151, 51))
        self.export_bt_2.setFont(font)
        self.export_bt_2.setObjectName("export_bt_2")
        self.export_bt_2.clicked.connect(self.export_file_web)
        self.select_driver_bt = QtWidgets.QPushButton(self.tab_2)
        self.select_driver_bt.setGeometry(QtCore.QRect(10, 0, 211, 51))
        self.select_driver_bt.setFont(font)
        self.select_driver_bt.setObjectName("select_driver_bt")
        self.select_driver_bt.clicked.connect(self.file_selected)
        self.tabWidget_3.addTab(self.tab_6, "")
        self.tabWidget.addTab(self.tab_2, "")
        EZ_Scrap.setCentralWidget(self.centralwidget)

        self.retranslateUi(EZ_Scrap)
        QtCore.QMetaObject.connectSlotsByName(EZ_Scrap)

        self.update_search_word()

        self.qTimer.start()

        self.confirm = False

        self.tweets = pd.DataFrame()

    def retranslateUi(self, EZ_Scrap):
        _translate = QtCore.QCoreApplication.translate
        EZ_Scrap.setWindowTitle(_translate("EZ_Scrap", "Ez_Scrap"))
        self.search_label.setText(_translate("EZ_Scrap", "Search"))
        self.search_bt.setText(_translate("EZ_Scrap", "Search"))
        self.label.setText(_translate("EZ_Scrap", "Start Date"))
        self.label_2.setText(_translate("EZ_Scrap", "End Date"))
        self.label_3.setText(_translate("EZ_Scrap", "Search Word"))
        self.label_4.setText(_translate("EZ_Scrap", "Status : standby"))
        self.label_5.setText(_translate("EZ_Scrap", "Status : standby"))
        self.search_bt_2.setText(_translate("EZ_Scrap", "Search"))
        self.scrap_bt.setText(_translate("EZ_Scrap", "Scrap"))
        self.select_driver_bt.setText(_translate("EZ_Scrap", "Select Driver"))
        self.positive_label.setText(_translate("EZ_Scrap", "Positive"))
        self.neutral_label.setText(_translate("EZ_Scrap", "Neutral"))
        self.negative_label.setText(_translate("EZ_Scrap", "Negative"))
        self.label_8.setText(_translate("EZ_Scrap", "100%"))
        self.label_9.setText(_translate("EZ_Scrap", "100%"))
        self.label_10.setText(_translate("EZ_Scrap", "100%"))
        self.label_11.setText(_translate("EZ_Scrap", "100%"))
        self.label_12.setText(_translate("EZ_Scrap", "100%"))
        self.label_13.setText(_translate("EZ_Scrap", "100%"))
        self.positive_label_2.setText(_translate("EZ_Scrap", "Positive"))
        self.neutral_label_2.setText(_translate("EZ_Scrap", "Neutral"))
        self.negative_label_2.setText(_translate("EZ_Scrap", "Negative"))
        self.export_bt.setText(_translate("EZ_Scrap", "Export"))
        self.export_bt_2.setText(_translate("EZ_Scrap", "Export"))
        self.related_label.setText(_translate("EZ_Scrap", "Related words"))
        self.sentiment_label.setText(_translate("EZ_Scrap", "Sentiment"))
        self.sentiment_label2.setText(_translate("EZ_Scrap", "Sentiment"))
        self.related_label_2.setText(_translate("EZ_Scrap", "Related words"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("EZ_Scrap", "Twitter"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("EZ_Scrap", "Website"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_3), _translate("EZ_Scrap", "Data"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_4), _translate("EZ_Scrap", "Stat"))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_5), _translate("EZ_Scrap", "Data"))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_6), _translate("EZ_Scrap", "Stat"))

    def update_status(self):
        tweet_status = self.tw_crawler.get_status()
        web_status = self.web_crawler.get_status()
        
        self.label_4.setText(f"Status : {tweet_status}")
        self.label_5.setText(f"Status : {web_status}")
        
        self.update_search_word()

    def confirm_scrap_popup(self):
        popup = QtWidgets.QMessageBox()
        popup.setWindowTitle("Confirm scrap")
        popup.setText("No keyword in database do you want to scrap?")
        popup.setIcon(QtWidgets.QMessageBox.Question)
        popup.setStandardButtons(QtWidgets.QMessageBox.Ok|QtWidgets.QMessageBox.Cancel)
        popup.buttonClicked.connect(self.popup_button)
        x = popup.exec_()

    def confirm_date_scrap_popup(self,start_day,end_day):
        popup = QtWidgets.QMessageBox()
        popup.setWindowTitle("Confirm scrap")
        popup.setText(f"This keyword have no data between {start_day} - {end_day}?")
        popup.setIcon(QtWidgets.QMessageBox.Question)
        popup.setStandardButtons(QtWidgets.QMessageBox.Ok|QtWidgets.QMessageBox.Cancel)
        popup.buttonClicked.connect(self.popup_button)
        x = popup.exec_()

    def no_text_in_keyword(self):
        popup = QtWidgets.QMessageBox()
        popup.setWindowTitle("Error")
        popup.setText("Please enter text before search")
        popup.setIcon(QtWidgets.QMessageBox.Critical)
        popup.setStandardButtons(QtWidgets.QMessageBox.Ok)
        popup.buttonClicked.connect(lambda:popup.close())
        x = popup.exec_()
    
    def popup_button(self , i):
        if i.text() == "OK":
            self.confirm = True
        else:
            self.confirm = False
    
    def update_search_word(self):
        self.listWidget.clear()
        self.search_word = os.listdir("./data/tweets")
        for word in self.search_word:
            self.listWidget.addItem(word)

    def scrap(self):
        self.web_worker = WebWorker_Scrap(self.web_crawler)
        self.web_worker.start()

    def search_tweet(self):
        start_day = self.start_date.date().toPyDate() 
        end_day = self.end_date.date().toPyDate()
        keyword = self.lineEdit.text()
        exist = False
        self.tw_worker = TweetWorker(keyword,start_day,end_day,self.tw_crawler)

        if keyword == "":
            self.no_text_in_keyword()

        elif keyword not in self.search_word and keyword != "":
            self.confirm_scrap_popup()
        else:
            exist = True
            while start_day >= end_day:
                if start_day.strftime('%Y-%m-%d') not in self.tw_crawler.metadata['twitter-keyword'][keyword]['date']:
                    exist = False
                    self.confirm_date_scrap_popup(start_day,end_day)
                    break
                start_day -= timedelta(1)
        if self.confirm and (not TweetWorker.running):
            self.tw_worker.start()
            self.update_search_word()
        if exist:
            self.get_tweets()
    
    def search_web(self):
        keyword = self.lineEdit_2.text()
        self.web_worker = WebWorker_Search(keyword,self.web_crawler)
        self.web_worker.finished.connect(lambda:self.set_grid_table_web(self.web_worker.data))
        self.web_worker.start()

    
    def set_grid_table_tweet(self,data):
        self.table.setRowCount(data.shape[0])
        self.table.setColumnCount(data.shape[1])
        self.table.setHorizontalHeaderLabels(data.columns)

        for row in data.iterrows():
            values = row[1]
            for col_index,value in enumerate(values):
                tableItem = QtWidgets.QTableWidgetItem(str(value))
                self.table.setItem(row[0],col_index,tableItem)
    
    def set_grid_table_web(self,data):
        # data
        self.table_2.setRowCount(data[0].shape[0])
        self.table_2.setColumnCount(data[0].shape[1])
        self.table_2.setHorizontalHeaderLabels(data[0].columns)

        for row in data[0].iterrows():
            values = row[1]
            for col_index,value in enumerate(values):
                tableItem = QtWidgets.QTableWidgetItem(str(value))
                self.table_2.setItem(row[0],col_index,tableItem)
        # count word
        self.related_table_2.setRowCount(30)
        self.related_table_2.setColumnCount(2)
        self.related_table_2.setHorizontalHeaderLabels(["Word","Count"])
        
        for row, item in enumerate(data[1].most_common(30)):
            self.related_table_2.setItem(row,0,QtWidgets.QTableWidgetItem(item[0]))
            self.related_table_2.setItem(row,1,QtWidgets.QTableWidgetItem(str(item[1])))
        # sentiment 
        pos = data[0]['Positive'].sum()
        neu = data[0]['Neutral'].sum()
        neg = data[0]['Negative'].sum()
        sum = pos + neu + neg
        self.label_11.setText(f'{(pos/sum*100):.2f} %')
        self.label_12.setText(f'{(neu/sum*100):.2f} %')
        self.label_13.setText(f'{(neg/sum*100):.2f} %')
    
    def showItem(self):
        self.lineEdit.setText(self.listWidget.selectedItems()[0].text())
        self.get_all_tweets()
    
    def get_all_tweets(self):
        keyword = self.lineEdit.text()
        file_list = os.listdir(f"./data/tweets/{keyword}")
        df_list = []
        for day in file_list:
            df = pd.read_excel(f"./data/tweets/{keyword}/{day}",engine="openpyxl")
            df_list.append(df)
        tweets = pd.concat(df_list, ignore_index=True)
        tweets = tweets.sort_values("post date")
        self.set_grid_table_tweet(tweets)
        self.show_sentiment(tweets)
        count_word = self.find_related_word(tweets,keyword)
        self.show_related_word(count_word)

    def get_tweets(self):
        start_day = self.start_date.date().toPyDate() 
        end_day = self.end_date.date().toPyDate()

        keyword = self.lineEdit.text()
        file_list = os.listdir(f"./data/tweets/{keyword}")
        df_list = []
        while start_day >= end_day:
            day = date.strftime(start_day,'%Y-%m-%d')
            if f"{day}.xlsx" in file_list:
                df = pd.read_excel(f"./data/tweets/{keyword}/{day}.xlsx",engine="openpyxl")
                df_list.append(df)
            start_day -= timedelta(1)
        self.tweets = pd.concat(df_list, ignore_index=True)
        self.tweets = self.tweets.sort_values("post date")
        count_word = self.find_related_word(self.tweets,keyword)
        self.set_grid_table_tweet(self.tweets)
        self.show_sentiment(self.tweets)
        self.show_related_word(count_word)

    def show_sentiment(self,data):
        sentiment = data["sentiment"].value_counts()
        neutral = sentiment["neutral"]
        positive = sentiment["positive"]
        negative = sentiment["negative"]

        self.label_8.setText(f"{((positive/sentiment.sum())*100):.2f} %")
        self.label_9.setText(f"{((neutral/sentiment.sum())*100):.2f} %")
        self.label_10.setText(f"{((negative/sentiment.sum())*100):.2f} %")

    def del_stopword(self,text):
        text = re.sub("\d+", "", text)
        text_tokens = word_tokenize(text)
        text = [word for word in text_tokens if not word.lower() in stopwords.words("english")]
        real_text = []
        for word in text:
            if len(word) == 1:
                continue
            real_text.append(word)
        text = ' '.join(real_text)

        return text
    
    def del_stopword_th(self,text):
        stopwords = list(thai_stopwords())
        text_token = token_th(text,keep_whitespace=False,engine="longest")
        text = [word for word in text_token if word not in stopwords]
        return text
         
    def cleanText_th(tweet_text : list) -> list:
        def get_cleantext(text : str,index : int):

            text = re.sub('http://\S+|https://\S+', '', text) # remove url


            url = "https://api.aiforthai.in.th/textcleansing" #api for remove emoji
            
            params = {f'text':{text}}
            
            
            headers = {
                'Apikey': "fIwWRjuLjs8KrK8BcA7kaj5das47eZpH",
                }
            
            response = requests.request("GET", url, headers=headers, params=params)
            cleantext[index] = response.json()['cleansing_text']

        n = len(tweet_text)
        cleantext = [None] * n
        with ThreadPoolExecutor(max_workers=n) as executor:
            executor.map(get_cleantext, tweet_text, list(range(n)))
            executor.shutdown(wait=True)
    
    
        return cleantext
    
    def find_related_word(self,data,keyword) -> Counter:
        count_word = Counter()
        reg = re.compile(r'[a-zA-Z]')
        if reg.match(keyword.replace("#","")):
            for tweet in data["tweet"]:
                text = self.del_stopword(str(tweet))
                count_word += Counter(text.split(' '))
            for list in data["hashtag"]:
                count_word += Counter(eval(list))
            count_word[keyword] = 0
            count_word[keyword.lower()] = 0
            count_word[keyword.upper()] = 0
            count_word[keyword.replace('#','')] = 0
            count_word[keyword.replace('#','').lower()] = 0
            count_word[keyword.replace('#','').upper()] = 0
        else:
            pattern = re.compile(r"[^\u0E00-\u0E7F]")
            textlist = cleanText_th(data["tweet"])
            realtext = []
            for text in textlist:
                text = re.sub(pattern,"",str(text))
                text = self.del_stopword_th(text)
                for word in text:
                    if len(word) == 1:
                        continue
                    realtext.append(word)
                count_word += Counter(realtext)
            for hashtag in data["hashtag"]:
                try:
                    count_word += Counter(eval(hashtag))
                except:
                    continue
            
        return count_word
    
    def show_related_word(self,count_word):
        self.related_table.setRowCount(30)
        self.related_table.setColumnCount(2)
        self.related_table.setHorizontalHeaderLabels(["Word","Count"])
        
        for row,item in enumerate(count_word.most_common(30)):
            self.related_table.setItem(row,0,QtWidgets.QTableWidgetItem(item[0]))
            self.related_table.setItem(row,1,QtWidgets.QTableWidgetItem(str(item[1])))


    def file_selected(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_path = QtWidgets.QFileDialog.getOpenFileName()
        self.web_crawler.set_selenium_webdriver(file_path[0])
    
    def export_file_tweet(self):
        file_filter = 'Excel File (*.xlsx)'
        response = QtWidgets.QFileDialog.getSaveFileName(
            caption='Export file',
            filter=file_filter,
            initialFilter='Excel File (*.xlsx)'
        )
        if not self.tweets.empty:
            df = self.tweets.iloc[:, [0,1,2,3,5,6,8]]
            df.to_excel(response[0],engine="openpyxl", index=False)
    
    def export_file_web(self):
        file_filter = 'Excel File (*.xlsx)'
        response = QtWidgets.QFileDialog.getSaveFileName(
            caption='Export file',
            filter=file_filter,
            initialFilter='Excel File (*.xlsx)'
        )
        if not self.web_worker.data.empty:
            df = self.web_worker.data.iloc[:, 0:-1]
            df.to_excel(response[0],engine="openpyxl", index=False)
    

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    EZ_Scrap = QtWidgets.QMainWindow()
    ui = Ui_EZ_Scrap()
    ui.setupUi(EZ_Scrap)
    EZ_Scrap.show()
    sys.exit(app.exec_())
