from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt5 import QtCore, QtGui, QtWidgets
import sys, re, urllib, json, webbrowser
import http.cookiejar as cookielib
import urllib.request
from urllib.parse import quote


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(964, 752)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(30, 90, 311, 31))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.lineEdit.setFont(font)
        self.lineEdit.setObjectName("lineEdit")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(360, 90, 131, 41))
        self.pushButton.setObjectName("pushButton")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(520, 100, 341, 31))
        self.label.setObjectName("label")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(40, 170, 861, 521))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 964, 21))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action = QtWidgets.QAction(MainWindow)
        self.action.setObjectName("action")
        self.menu.addAction(self.action)
        self.menubar.addAction(self.menu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Parser"))
        self.lineEdit.setPlaceholderText(_translate("MainWindow", "Введите запрос"))
        self.pushButton.setText(_translate("MainWindow", "Найти"))
        self.label.setText(_translate("MainWindow", "Все системы функционируют нормально."))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "название"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "подписчики"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "url"))
        self.menu.setTitle(_translate("MainWindow", "Файл"))
        self.action.setText(_translate("MainWindow", "Очистить"))


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.pushButton.clicked.connect(self.search)
        self.tableWidget.cellDoubleClicked.connect(self.open_url)

    def open_url(self, row, column):
        if column != 2:
            return
        url = self.tableWidget.item(row, column).text()
        webbrowser.open('http://' + url, new=1)

    def search(self):
        que = self.lineEdit.text().strip()
        if not que:
            self.label.setText('Пустой запрос')
        que = '+'.join(que.split())

        cj = cookielib.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-agent',
                              'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36')]
        try:
            content = opener.open(
                f'http://www.youtube.com/results?search_query={quote(que)}&sp=EgIQAg%253D%253D').read()
        except Exception as e:
            self.label.setText(str(e))
            quit()
        obj = re.findall(r'window\["ytInitialData"\] = (.*?)};',
                         content.decode('utf-8'))
        obj[0] += '}'
        # obj[0] = str(obj[0]).replace(r"'", r"\'")
        # print(obj[0])
        try:
            # data = json.dumps(obj[0])
            data = json.loads(obj[0])
            res = []
            for i in \
                    data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer'][
                        'contents'][0][
                        'itemSectionRenderer']['contents']:
                try:
                    num = i['channelRenderer']['subscriberCountText']['simpleText']
                    if 'подпис' not in num and 'subs' not in num:
                        continue
                    num = ' '.join(num.split()[:-1])
                    channel_url = i['channelRenderer']['navigationEndpoint']['commandMetadata']['webCommandMetadata'][
                        'url']
                    channel_name = i['channelRenderer']['title']['simpleText']
                    if num and channel_name and 'channel' in channel_url:
                        res.append((channel_name, num, channel_url))
                except (KeyError, IndexError):
                    continue

        except Exception as e:
            self.label.setText("Введите другой запрос. Произошла ошибка")
            return
        self.tableWidget.setRowCount(0)
        for channel_name, num, channel_url in res:
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 0, QTableWidgetItem(channel_name))
            self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 1, QTableWidgetItem(num))
            self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 2,
                                     QTableWidgetItem('www.youtube.com' + channel_url))
        self.tableWidget.resizeColumnsToContents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
