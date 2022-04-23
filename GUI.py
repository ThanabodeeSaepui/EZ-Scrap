from PyQt5 import QtCore, QtGui, QtWidgets
from datetime import date
from spider import *

class TweetWorker(QtCore.QThread):
    running = False
    def __init__(self, keyword,startday,endday,tw_crawler):
        QtCore.QThread.__init__(self)
        self.keyword , self.start_day, self.end_day = keyword , startday , endday
        self.tw_crawler = tw_crawler
    # progress = QtCore.pyqtSignal()
    # finished = QtCore.pyqtSignal()

    def run(self):
        TweetWorker.running = True
        self.tw_crawler.search_tweets(self.keyword,self.start_day,self.end_day)
        TweetWorker.running = False
        # self.progress.emit()
        # self.finished.emit()

class WebWorker(QtCore.QThread):
    def __init__(self,web_crawler):
        QtCore.QThread.__init__(self)
        self.web_crawler = web_crawler
    # progress = QtCore.pyqtSignal()
    # finished = QtCore.pyqtSignal()

    def run(self):
        self.web_crawler.default_scrap()
        # self.progress.emit()
        # self.finished.emit()


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
        self.lineEdit = QtWidgets.QLineEdit(self.tab)
        self.lineEdit.setGeometry(QtCore.QRect(470, 20, 651, 20))
        self.lineEdit.setObjectName("lineEdit")
        self.search_bt = QtWidgets.QPushButton(self.tab)
        self.search_bt.setGeometry(QtCore.QRect(1140, 10, 81, 41))
        self.search_bt.setFont(font)
        self.search_bt.setObjectName("search_bt")
        self.search_bt.clicked.connect(self.search_tweet)
        self.table = QtWidgets.QTableWidget(self.tab)
        self.table.setGeometry(QtCore.QRect(220, 90, 1051, 621))
        self.table.setObjectName("tableView")
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
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.table_2 = QtWidgets.QTableWidget(self.tab_2)
        self.table_2.setGeometry(QtCore.QRect(10, 110, 1261, 611))
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
        self.select_driver_bt = QtWidgets.QPushButton(self.tab_2)
        self.select_driver_bt.setGeometry(QtCore.QRect(10, 0, 211, 51))
        self.select_driver_bt.setFont(font)
        self.select_driver_bt.setObjectName("select_driver_bt")
        self.select_driver_bt.clicked.connect(self.file_selected)
        self.tabWidget.addTab(self.tab_2, "")
        EZ_Scrap.setCentralWidget(self.centralwidget)

        self.retranslateUi(EZ_Scrap)
        QtCore.QMetaObject.connectSlotsByName(EZ_Scrap)

        self.update_search_word()

        self.qTimer.start()

        self.confirm = False

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
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("EZ_Scrap", "Twitter"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("EZ_Scrap", "Website"))

    def update_status(self):
        tweet_status = self.tw_crawler.get_status()
        web_status = self.web_crawler.get_status()
        self.label_4.setText(f"Status : {tweet_status}")
        self.label_5.setText(f"Status : {web_status}")

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
        self.web_worker = WebWorker(self.web_crawler)
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
        data = self.web_crawler.search_web(keyword)
        self.set_grid_table_web(data)

    
    def set_grid_table_tweet(self,data):
        self.table.setRowCount(data.shape[0])
        self.table.setColumnCount(data.shape[1])
        self.table.setHorizontalHeaderLabels(data.columns)

        for row in data.iterrows():
            values = row[1]
            for col_index,value in enumerate(values):
                tableItem = QtWidgets.QTableWidgetItem(str(value))
                self.table.setItem(row[0],col_index,tableItem)
        self.table.setColumnWidth(3,120)
        self.table.setColumnWidth(4,1000)
        self.table.setColumnWidth(8,340)
    
    def set_grid_table_web(self,data):
        self.table_2.setRowCount(data.shape[0])
        self.table_2.setColumnCount(data.shape[1])
        self.table_2.setHorizontalHeaderLabels(data.columns)

        for row in data.iterrows():
            values = row[1]
            for col_index,value in enumerate(values):
                tableItem = QtWidgets.QTableWidgetItem(str(value))
                self.table_2.setItem(row[0],col_index,tableItem)
        # self.table_2.setColumnWidth(3,120)
        # self.table_2.setColumnWidth(4,1000)
        # self.table_2.setColumnWidth(8,340)
    
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
        tweets = pd.concat(df_list, ignore_index=True)
        tweets = tweets.sort_values("post date")
        self.set_grid_table_tweet(tweets)

    def file_selected(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_path = QtWidgets.QFileDialog.getOpenFileName()
        self.web_crawler.set_selenium_webdriver(file_path[0])
    

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    EZ_Scrap = QtWidgets.QMainWindow()
    ui = Ui_EZ_Scrap()
    ui.setupUi(EZ_Scrap)
    EZ_Scrap.show()
    sys.exit(app.exec_())
