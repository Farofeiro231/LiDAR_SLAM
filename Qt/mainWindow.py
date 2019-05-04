import sys, time
from numpy.random import randn
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow, QDockWidget
from PyQt5.QtChart import QScatterSeries, QChart, QChartView, QValueAxis

from PyQt5.QtCore import QTimer, QPointF, Qt 

class Window(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.title = "My visualization app"
        self.left = 10
        self.top = 10
        self.height = 480
        self.width = 640
        self.count = 0
        self.time = 0
        self.label = QLabel(self)
        
        dock = QDockWidget("!!", self)
        dock.setWidget(self.label)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        self.chart = QChart()
        self.config_axis()
        self.series = QScatterSeries()
        self.config_series()
        self.update()
        self.timer = QTimer(self)
        self.view = QChartView(self.chart)
        self.setCentralWidget(self.view)  # It is needed to create to view because the CentralWidget needs to be a QWidget, and a QChart is not so.
        self.initWindow()


    def config_series(self):
        self.series.setMarkerSize(10)
        self.label.move(15, 15)

    def config_axis(self):
        self.xAxis = QValueAxis()
        self.yAxis = QValueAxis()
        self.xAxis.setRange(0, 100)
        self.xAxis.setTitleText("Eixo x")
        self.yAxis.setRange(0, 100)
        self.yAxis.setTitleText("Eixo y")
        self.chart.addAxis(self.xAxis, Qt.AlignBottom)
        self.chart.addAxis(self.yAxis, Qt.AlignLeft)

    

    def update(self):
        self.label.setText("FPS: {:.2f}".format(1/(time.time()-self.time)))
        self.time = time.time()
        a = []
        a.append([QPointF(50 + 10 * randn(), 50 + 10 * randn()) for i in range(10)])
        if self.count == 0:
            self.series.append(a[0][:])
        else:
            self.series.replace(a[0][:])
            #self.chart.createDefaultAxes()
        self.count += 1
        end = time.time()


    
    def initWindow(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)
        self.chart.addSeries(self.series)
        self.series.attachAxis(self.xAxis)
        self.series.attachAxis(self.yAxis)
        #self.chart.createDefaultAxes()
        self.timer.timeout.connect(self.update)
        self.timer.start(0)
        self.show()


if __name__ == "__main__":

    myApp = QApplication(sys.argv)

    myWindow = Window()

    sys.exit(myApp.exec_())
