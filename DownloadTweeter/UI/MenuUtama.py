import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
import multiprocessing

import threading
 
from Algoritma import GrabTwitter

class App(QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = 'Download data Twitter'
        self.left = 10
        self.top = 10
        self.initUI()

        #''' testing
        self.textbox.setText("kalimantan, jawa")
        self.textboxMaxTweet.setText("20")
        self.textboxTimeLimit.setText("10")
        self.textboxLatitude.setText("-6.2891084")
        self.textboxLongitude.setText("106.7560364")
        self.textboxRadius.setText("1000km")

        #'''
 
    def initUI(self):
        self.setWindowTitle(self.title)
        self.center()
        self.setFixedSize(700 ,700)  

        lbl1 = QLabel("Masukan Query anda, untuk melakukan penelusuran perbagian anda bisa menggunakan tanda koma (,)", self)
        lbl1.move(10,10)
        lbl1.resize(self.frameGeometry().width() - 20, 20)

        #''' line pertama
        lblpencarian = QLabel("Pencarian : ", self)
        lblpencarian.move(10, 40)
        lblpencarian.resize(100,25)

        self.textbox = QLineEdit(self)
        self.textbox.move(lblpencarian.frameGeometry().x() + lblpencarian.frameGeometry().width() + 10, lblpencarian.frameGeometry().y())
        self.textbox.resize(self.frameGeometry().width() - 10 - 10 - 10 - lblpencarian.frameGeometry().width(), lblpencarian.frameGeometry().height())
        #'''

        #''' line kedua
        lblmaxtweet = QLabel("Maximum Tweet: ", self)
        lblmaxtweet.move(lblpencarian.frameGeometry().x(), lblpencarian.frameGeometry().y() + 10 + lblpencarian.frameGeometry().height())
        lblmaxtweet.resize(lblpencarian.frameGeometry().width(), lblpencarian.frameGeometry().height())

        self.textboxMaxTweet = QLineEdit(self)
        self.textboxMaxTweet.move(10 + lblmaxtweet.frameGeometry().width() + 10, lblmaxtweet.frameGeometry().y())
        self.textboxMaxTweet.resize(self.frameGeometry().width() / 2 - lblmaxtweet.frameGeometry().width(), lblmaxtweet.frameGeometry().height())

        lbltimelimit = QLabel("Time Limit : ", self)
        lbltimelimit.move(self.textboxMaxTweet.frameGeometry().x() + self.textboxMaxTweet.frameGeometry().width() + 10, lblmaxtweet.frameGeometry().y())
        lbltimelimit.resize(lblpencarian.frameGeometry().width() - 3, lblpencarian.frameGeometry().height())

        self.textboxTimeLimit = QLineEdit(self)
        self.textboxTimeLimit.move(lbltimelimit.frameGeometry().x() + lbltimelimit.frameGeometry().width(), lbltimelimit.frameGeometry().y())
        self.textboxTimeLimit.resize(self.frameGeometry().width() - self.textboxTimeLimit.frameGeometry().x() - 10, lblmaxtweet.frameGeometry().height())
        #'''

        #''' line ketiga
        lblLatitude = QLabel("Latitude", self)
        lblLatitude.move(lblmaxtweet.frameGeometry().x(), lblmaxtweet.frameGeometry().y() + 10 + lblmaxtweet.frameGeometry().height())
        lblLatitude.resize(lblmaxtweet.frameGeometry().width(), lblmaxtweet.frameGeometry().height())

        self.textboxLatitude = QLineEdit(self)
        self.textboxLatitude.move(10 + lblLatitude.frameGeometry().width() + 10, lblLatitude.frameGeometry().y())
        self.textboxLatitude.resize((self.frameGeometry().width() - 50 - (lblLatitude.frameGeometry().width() * 2)) / 3, lblLatitude.frameGeometry().height())

        lblLongitude  = QLabel("Longitude ", self)
        lblLongitude.move(self.textboxLatitude.frameGeometry().x() + self.textboxLatitude.frameGeometry().width() + 10, lblLatitude.frameGeometry().y())
        lblLongitude.resize(lblmaxtweet.frameGeometry().width() / 2, lblmaxtweet.frameGeometry().height())

        self.textboxLongitude = QLineEdit(self)
        self.textboxLongitude.move(lblLongitude.frameGeometry().x() + lblLongitude.frameGeometry().width() + 10, lblLongitude.frameGeometry().y())
        self.textboxLongitude.resize(self.textboxLatitude.frameGeometry().width(), lblLatitude.frameGeometry().height())

        lblRadius = QLabel("Radius", self)
        lblRadius.move(self.textboxLongitude.frameGeometry().x() + self.textboxLongitude.frameGeometry().width() + 10 , lblLongitude.frameGeometry().y())
        lblRadius.resize(lblLongitude.frameGeometry().width(), lblLongitude.frameGeometry().height())

        self.textboxRadius = QLineEdit(self)
        self.textboxRadius.move(lblRadius.frameGeometry().x() + lblRadius.frameGeometry().width() + 10, lblRadius.frameGeometry().y())
        self.textboxRadius.resize(self.frameGeometry().width() - self.textboxRadius.frameGeometry().x() - 10, lblRadius.frameGeometry().height())

        #'''

        buttonGrabber = QPushButton("Grab Tweet", self)
        buttonGrabber.resize(self.frameGeometry().width() / 4,45)
        buttonGrabber.move(self.frameGeometry().width() - 10 - buttonGrabber.frameGeometry().width(), self.frameGeometry().height() - 10 - buttonGrabber.frameGeometry().height())

        self.listview = QListWidget(self)
        self.listview.move(lblLatitude.frameGeometry().x(), lblLatitude.frameGeometry().y() + lblLatitude.frameGeometry().height() + 10)
        self.listview.resize(self.frameGeometry().width() - 20, buttonGrabber.frameGeometry().y() - self.listview.frameGeometry().y() - 10)

        buttonGrabber.clicked.connect(self.on_click)

        self.show()

    def center(self):
        #self.setGeometry(self.left, self.top, self.width, self.height)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    @pyqtSlot()
    def on_click(self):
        jawab = QMessageBox.question(self, 'Pesan', 'Proses Download Data Twitter', QMessageBox.Yes)

        threadDownloadTwitter = ThreadDownloadTwitter(self.textbox.text(), self.textboxMaxTweet.text(), self.textboxTimeLimit.text(), self.textboxLatitude.text(), self.textboxLongitude.text(), self.textboxRadius.text())
        threadDownloadTwitter.update.connect(self.showMessage)

        if (jawab == QMessageBox.Yes):
            threadDownloadTwitter.start()
        return

    def showMessage(self, message):
        self.listview.addItem(message)
        #QMessageBox.question(self, "pesan", message, QMessageBox.Yes)



class ThreadCl(QThread):
    def __init__(self):
        return


class ThreadDownloadTwitter(QThread):
    update = pyqtSignal(str)
    
    def __init__(self, subreddits, maxtweet, timelimit, latitude, longtitude, radius):
        QThread.__init__(self)
        self.downloadTwitter = GrabTwitter.DownloadTweet()
        self.subreddits = subreddits
        self.downloadTwitter.max_tweets = int(maxtweet)
        self.downloadTwitter.time_limit = int(timelimit)
        self.downloadTwitter.JBD = ''.join([latitude, ",", longtitude, "," , radius])
        self.downloadTwitter.update = self.update

    def __del__(self):
        self.wait()

    def run(self):
        subreddits_list = str(self.subreddits).split(',')

        for subreddit in subreddits_list:
            self.downloadTwitter.run(subreddit)

