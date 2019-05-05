import multiprocessing as mp
import concurrent.futures
import sys, time
from numpy.random import randn
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow, QDockWidget
from PyQt5.QtChart import QScatterSeries, QChart, QChartView, QValueAxis

from PyQt5.QtCore import QTimer, QPointF, Qt 
import numpy as np
from functools import partial


class Window(QMainWindow):
    
    def __init__(self, pointsList, threadEvent):
        super().__init__()
        self.title = "Lidar data points"
        #self.queue = queue
        self.points2Plot = pointsList
        self.event = threadEvent
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
        #self.update()
        self.timer = QTimer(self)
        self.view = QChartView(self.chart)
        self.setCentralWidget(self.view)  # It is needed to create to view because the CentralWidget needs to be a QWidget, and a QChart is not so.
        self.initWindow()


    def config_series(self):
        myPen = self.series.pen()
        myPen.setWidthF(.6)
        self.series.setPen(myPen)
        self.series.setMarkerSize(5)
        self.label.move(15, 15)

    def config_axis(self):
        self.xAxis = QValueAxis()
        self.yAxis = QValueAxis()
        self.xAxis.setRange(-2000, 2000)
        self.xAxis.setTitleText("Eixo x")
        self.yAxis.setRange(-2000, 2000)
        self.yAxis.setTitleText("Eixo y")
        self.chart.addAxis(self.xAxis, Qt.AlignBottom)
        self.chart.addAxis(self.yAxis, Qt.AlignLeft)

    def add_points(points):
        self.points2Plot = points

    def update(self):#, points2Plot): 
        print("Passando a bola para ransac\n\n\n")
        self.event.wait()
        start = time.time()
        #self.points2Plot = self.queue.get(True)
        #fetch_time = time.time() - start
        #print("inside update...")
        self.label.setText("FPS: {:.2f}".format(1/(time.time()-self.time)))
        self.time = time.time()
        #tempSeries = self.queue.get(True)
        #a = []
        #a.append([QPointF(500 + 100 * randn(), 500 + 100 * randn()) for i in range(10)])
        if self.count == 0 and self.points2Plot != []:
            self.series.append(self.points2Plot[0][:])
            del self.points2Plot[:]
            self.count = 1
            #self.series.append(np.array(a[0][:]))
        elif self.points2Plot != []:
            #print(self.points2Plot)
            self.series.replace(self.points2Plot[0][:])
            del self.points2Plot[:]
            #self.series.replace(np.array(a[0][:]))
            #self.chart.createDefaultAxes()
        end = time.time()
        self.event.clear()
        #print("Fetch time: {:.7f}".format(fetch_time))
        #print("Elapsed time:{:.7f}".format(end-start))


    
    def initWindow(self):
        print("queue inside myWindow: {}".format(self.points2Plot))
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)
        self.chart.addSeries(self.series)
        self.series.attachAxis(self.xAxis)
        self.series.attachAxis(self.yAxis)
        self.timer.timeout.connect(self.update)
        self.timer.start(0)
        self.show()


def ploting(pairInliers, threadEvent):
    
    myApp = QApplication(sys.argv)
    print("My queue received by ploting: {}".format(pairInliers))
    myWindow = Window(pairInliers, threadEvent)

    sys.exit(myApp.exec_())


#if __name__ == "__main__":

#   myApp = QApplication(sys.argv)

#    myWindow = Window()

#    sys.exit(myApp.exec_())
