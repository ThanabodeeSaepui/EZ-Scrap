from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_EZ_Scrap(object):
    def setupUi(self, EZ_Scrap):
        font = QtGui.QFont()
        font.setPointSize(18)
        EZ_Scrap.setObjectName("EZ_Scrap")
        EZ_Scrap.resize(971, 600)
        self.centralwidget = QtWidgets.QWidget(EZ_Scrap)
        self.centralwidget.setObjectName("centralwidget")
        self.search_label = QtWidgets.QLabel(self.centralwidget)
        self.search_label.setGeometry(QtCore.QRect(20, 10, 101, 41))
        self.search_label.setFont(font)
        self.search_label.setObjectName("search_label")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(220, 20, 651, 20))
        self.lineEdit.setObjectName("lineEdit")
        self.search_bt = QtWidgets.QPushButton(self.centralwidget)
        self.search_bt.setGeometry(QtCore.QRect(880, 10, 81, 41))
        self.search_bt.setFont(font)
        self.search_bt.setObjectName("search_bt")
        self.search_bt.clicked.connect(self.confirm_scrap_popup)
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(110, 20, 81, 22))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setGeometry(QtCore.QRect(10, 80, 951, 511))
        self.listWidget.setObjectName("listWidget")
        EZ_Scrap.setCentralWidget(self.centralwidget)

        self.retranslateUi(EZ_Scrap)
        QtCore.QMetaObject.connectSlotsByName(EZ_Scrap)

    def retranslateUi(self, EZ_Scrap):
        _translate = QtCore.QCoreApplication.translate
        EZ_Scrap.setWindowTitle(_translate("EZ_Scrap", "Ez_Scrap"))
        self.search_label.setText(_translate("EZ_Scrap", "Search"))
        self.search_bt.setText(_translate("EZ_Scrap", "Search"))
        self.comboBox.setItemText(0, _translate("EZ_Scrap", "Twitter"))
        self.comboBox.setItemText(1, _translate("EZ_Scrap", "Web"))
    
    def confirm_scrap_popup(self):
        popup = QtWidgets.QMessageBox()
        popup.setWindowTitle("Confirm scrap")
        popup.setText("No keyword in database do you want to scrap?")
        popup.setIcon(QtWidgets.QMessageBox.Question)
        popup.setStandardButtons(QtWidgets.QMessageBox.Ok|QtWidgets.QMessageBox.Cancel)
        popup.buttonClicked.connect(self.popup_button)
        x = popup.exec_()
    
    def popup_button(self , i):
        print(i.text())

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    EZ_Scrap = QtWidgets.QMainWindow()
    ui = Ui_EZ_Scrap()
    ui.setupUi(EZ_Scrap)
    EZ_Scrap.show()
    sys.exit(app.exec_())
