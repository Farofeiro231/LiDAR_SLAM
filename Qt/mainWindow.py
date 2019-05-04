import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow
from PyQt5.QtCharts import QScatterSeries, QChart, QChartView
from PyQt5.QtCore import QTimer


class Window(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.title = "My visualization app"
        self.left = 100
        self.top = 100
        self.height = 480
        self.widht = 640
        self.chart = QChart()
        self.view = QChartView(self.chart)
        self.setCentralWidget(self.view)  # It is needed to create to view because the CentralWidget needs to be a QWidget, and a QChart is not so.
        self.initWindow()


    def config_chart(self):
        points = QScatterSeries(self)


    
    def initWindow(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)
        self.show()
