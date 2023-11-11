import os

from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QLineEdit, QVBoxLayout, QComboBox, QCompleter, \
    QListWidget, QListWidgetItem, QDialog, QHBoxLayout, QSizePolicy, QSplitter
import sqlite3


class ImageWindow(QDialog):
    def __init__(self, imgPath, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Card Viewer")
        self.setGeometry(100, 100, 400, 400)
        self.label = QLabel()
        self.label.setPixmap(QPixmap(imgPath))

        layout = QVBoxLayout()
        layout.addWidget(self.label)

        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trading App")
        # self.setFixedSize(1000, 1000)
        self.splitter = QSplitter()
        leftLayout = QVBoxLayout()
        rightLayout = QVBoxLayout()
        photoLayout = QVBoxLayout()

        self.label = QLabel()
        self.input = QLineEdit()
        self.resultList = QListWidget()
        self.filterBox = QComboBox()
        self.photo = QLabel()
        self.photo.setPixmap(QPixmap('Images\Placeholder.jpg'))

        policy = self.filterBox.sizePolicy()
        policy.setHorizontalPolicy(QSizePolicy.Expanding)
        self.filterBox.setSizePolicy(policy)

        photoLayout.addWidget(self.photo)
        leftLayout.addLayout(photoLayout)
        leftLayout.addStretch(1)
        rightLayout.addWidget(self.input)
        rightLayout.addWidget(self.filterBox)
        rightLayout.addWidget(self.label)
        rightLayout.addWidget(self.resultList)

        leftWidget = QWidget()
        leftWidget.setLayout(leftLayout)
        rightWidget = QWidget()
        rightWidget.setLayout(rightLayout)

        self.splitter.addWidget(leftWidget)
        self.splitter.addWidget(rightWidget)

        self.setCentralWidget(self.splitter)

        self.conn = sqlite3.connect('data.db')
        self.cur = self.conn.cursor()
        query = 'SELECT Name, Card_Set, Price FROM Cards'
        results = self.cur.execute(query).fetchall()

        names = [f"{result[0]} | {result[1]} | ${result[2]}" for result in results]

        completer = QCompleter(names)
        self.input.setCompleter(completer)
        completer.setCaseSensitivity(2)

        completer.activated.connect(self.updateLabel)
        self.resultList.itemClicked.connect(self.resultItemClicked)
        self.filterBox.activated.connect(self.filter)

    def openCardView(self, imgPath):
        img = ImageWindow(imgPath, self)
        img.exec()

    def updateLabel(self):
        user_input = self.input.text()
        name = user_input.split("|")[0].strip()
        cset = user_input.split("|")[1].lstrip().rstrip()
        imgPath = os.path.join("Images", cset, f"{name}.jpg")
        self.photo.setPixmap(QPixmap(imgPath))

        price = user_input.split("$")[-1]
        query = 'SELECT Name, Card_Set, Price FROM Cards ' \
                'WHERE Price BETWEEN ? * .90 AND ? * 1.1 AND Card_Set NOT LIKE "%Promo%" ' \
                'ORDER BY Card_Set, Price'
        res = self.cur.execute(query, (price, price)).fetchall()
        self.filterBox.clear()
        self.resultList.clear()
        self.filterBox.addItem("All")
        seen = []

        for row in res:
            name, cardSet, price = row
            text = f"{name} - {cardSet} - ${price}"
            imgPath = os.path.join("Images", cardSet, f"{name}.jpg")
            if cardSet not in seen:
                seen.append(cardSet)
                self.filterBox.addItem(cardSet)
            item = QListWidgetItem(text)
            item.imgPath = imgPath
            self.resultList.addItem(item)

    def filter(self):
        user_input = self.input.text()
        price = user_input.split("$")[-1]
        userFilter = self.filterBox.currentText()
        if userFilter == 'All':
            self.updateLabel()
        else:

            query = 'SELECT Name, Card_Set, Price FROM Cards ' \
                    'WHERE Price BETWEEN ? * .90 AND ? * 1.1 AND Card_Set NOT LIKE "%Promo%" ' \
                    'AND Card_SET = ?' \
                    'ORDER BY Card_Set, Price'
            res = self.cur.execute(query, (price, price, userFilter)).fetchall()
            self.resultList.clear()
            seen = []
            for row in res:
                name, cardSet, price = row
                text = f"{name} - {cardSet} - ${price}"
                imgPath = os.path.join("Images", cardSet, f"{name}.jpg")
                if cardSet not in seen and cardSet != self.filterBox.currentText():
                    seen.append(cardSet)
                    self.filterBox.addItem(cardSet)
                item = QListWidgetItem(text)
                item.imgPath = imgPath
                self.resultList.addItem(item)

    def resultItemClicked(self, item):
        print(item.imgPath)
        self.openCardView(item.imgPath)


app = QApplication([])
window = MainWindow()
window.showMaximized()
app.setWindowIcon(QIcon(os.path.join("Images", 'pball.ico')))
window.setWindowIcon(QIcon(os.path.join("Images", 'pball.ico')))
app.exec()
