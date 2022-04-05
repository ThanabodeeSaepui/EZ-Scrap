from spider import *
from GUI import *
import sys

if __name__ == '__main__':
    # webcrawler = WebCrawler()
    # webcrawler.scrap()

    app = QtWidgets.QApplication(sys.argv)
    EZ_Scrap = QtWidgets.QMainWindow()
    ui = Ui_EZ_Scrap()
    ui.setupUi(EZ_Scrap)
    EZ_Scrap.show()
    sys.exit(app.exec_())
