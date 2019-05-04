import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon



class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = "My First Window"
        self.timer = QTimer(self)
        self.label = QLabel(self)
        self.left = 10
        self.top = 10
        self.height = 480
        self.width = 640
        self.initUI()
        self.count = 0

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.timer.timeout.connect(self.update)
        self.timer.start(10)
        self.show()
    
    def update(self):
        self.label.setText("Lol:{}".format(self.count))
        self.label.move(self.count, self.count)
        print("lol")
        self.count +=1



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
