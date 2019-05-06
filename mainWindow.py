import multiprocessing as mp
import concurrent.futures
import sys, time
from numpy.random import randn
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow, QDockWidget, QCheckBox
from PyQt5.QtChart import QScatterSeries, QChart, QChartView, QValueAxis

from PyQt5.QtCore import QTimer, QPointF, Qt, QObject
from PyQt5.QtGui import QGridLayout
import numpy as np
from functools import partial


XRANGE = 4000
YRANGE = 4000

class Window(QMainWindow):
    
    def __init__(self, landmarkPoints, allPoints, threadEvent):
        super().__init__()
        self.title = "Lidar data points"
        #self.queue = queue
        self.color = Qt.darkRed
        self.lmrkPoints = landmarkPoints
        self.allPoints = allPoints
        self.event = threadEvent
        self.left = 500
        self.top = 500
        self.height = 480
        self.width = 640
        self.count = 0
        self.time = 0

        self.label = QLabel(self)
        self.lmrkBox = QCheckBox("Landmark points", self)
        self.ptsBox = QCheckBox("Data points", self)

        self.boxArea = QWidget()
        self.mainLayout = QGridLayout()
        self.mainLayout.addWidget(self.lmrkBox, 0, 0)
        self.mainLayout.addWidget(self.ptsBox, 1, 0)
        self.mainLayout.setVerticalSpacing(5)
        self.boxArea.setLayout(self.mainLayout)
        crote = QDockWidget("Hide", self)
        crote.setWidget(self.boxArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, crote)

        dock = QDockWidget("", self)
        dock.setWidget(self.label)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        self.chart = QChart()
        self.config_axis()
        self.series = QScatterSeries(self.chart)
        self.allSeries = QScatterSeries(self.chart)
        self.config_series()
        #self.update()
        self.timer = QTimer(self)
        self.view = QChartView(self.chart)
        self.setCentralWidget(self.view)  # It is needed to create to view because the CentralWidget needs to be a QWidget, and a QChart is not so.
        self.initWindow()


    def config_series(self):
        self.series.setName("Landmark Points")
        self.allSeries.setName("Data Points")
        
        lmrkPen = self.series.pen()
        pen = self.allSeries.pen() 
        lmrkPen.setWidthF(.2)
        pen.setWidthF(.2)
        self.series.setPen(lmrkPen)
        self.allSeries.setPen(pen)

        self.series.setColor(Qt.red)
        self.allSeries.setColor(Qt.blue)
        
        self.series.setMarkerShape(1)  # 1 - rectangle; 0 - circle
        
        # for good visualization, the landmark points should be bigger than normal points
        
        self.series.setMarkerSize(8)
        self.allSeries.setMarkerSize(5)
        self.label.move(15, 15)

    def config_axis(self):
        self.xAxis = QValueAxis()
        self.yAxis = QValueAxis()
        self.xAxis.setRange(-XRANGE, XRANGE)
        self.xAxis.setTitleText("Eixo x")
        self.yAxis.setRange(-YRANGE, YRANGE)
        self.yAxis.setTitleText("Eixo y")
        self.chart.addAxis(self.xAxis, Qt.AlignBottom)
        self.chart.addAxis(self.yAxis, Qt.AlignLeft)

    def update(self):#, lmrkPoints): 
        #a = time.time()
        #print("Passando a bola para ransac\n\n\n")
        #print("Tempo:{:.8f}".format(time.time()-a))
        self.event.wait()
        start = time.time()
        #self.lmrkPoints = self.queue.get(True)
        #fetch_time = time.time() - start
        #print("inside update...")
        self.label.setText("FPS: {:.2f}".format(1/(time.time()-self.time)))
        self.time = time.time()
        #tempSeries = self.queue.get(True)
        #a = []
        #a.append([QPointF(500 + 100 * randn(), 500 + 100 * randn()) for i in range(10)])
        if self.count == 0 and self.lmrkPoints != []:
            self.series.append(self.lmrkPoints[0][:])
            self.allSeries.append(self.allPoints[0][:])
            del self.lmrkPoints[:]
            del self.allPoints[:]
            self.count = 1
            #self.series.append(np.array(a[0][:]))
        elif self.lmrkPoints != []:
            self.series.replace(self.lmrkPoints[0][:])
            self.allSeries.replace(self.allPoints[0][:])
            del self.lmrkPoints[:]
            del self.allPoints[:]
            #self.series.replace(np.array(a[0][:]))
            #self.chart.createDefaultAxes()
        end = time.time()
        self.event.clear()
        #print("Fetch time: {:.7f}".format(fetch_time))
        #print("Elapsed time:{:.7f}".format(end-start))

    def hide_show_points(self):
        self.series.setVisible(not self.series.isVisible())
    
    def hide_show_all_points(self):
        self.allSeries.setVisible(not self.allSeries.isVisible())
    
    def initWindow(self):
        print("queue inside myWindow: {}".format(self.lmrkPoints))
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)
        self.chart.addSeries(self.series)
        self.chart.addSeries(self.allSeries)
        self.series.attachAxis(self.xAxis)
        self.series.attachAxis(self.yAxis)
        self.allSeries.attachAxis(self.xAxis)
        self.allSeries.attachAxis(self.yAxis)
        
        self.timer.timeout.connect(self.update)
        self.lmrkBox.stateChanged.connect(self.hide_show_points)
        self.ptsBox.stateChanged.connect(self.hide_show_all_points)

        self.timer.start(0)
        self.show()


def ploting(pairInliers, allPoints, threadEvent):
    
    myApp = QApplication(sys.argv)
    print("My queue received by ploting: {}".format(pairInliers))
    myWindow = Window(pairInliers, allPoints, threadEvent)

    sys.exit(myApp.exec_())


#if __name__ == "__main__":

#   myApp = QApplication(sys.argv)

#    myWindow = Window()

#    sys.exit(myApp.exec_())
