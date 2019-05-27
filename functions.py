from lidar import Lidar
import numpy as np
import time
from PyQt5.QtCore import QPointF


PI = np.pi
DISTANCE_LIMIT = 30  # maximum tolerable distance between two points - in mm - for them to undergo RANSAC
ANGLE_TO_RAD = PI / 180
MIN_NEIGHBOORS = 50 # minimum number of points to even be considered for RANSAC processing


#  Configuring the figure subplots to hold the point cloud plotting. Mode can be rectilinear of polar
def config_plot(figure, lin=1, col=1, pos=1, mode="rectilinear"):
    ax = figure.add_subplot(lin, col, pos, projection=mode)
    ax.autoscale(False)
    ax.set_xlabel("X axis")
    ax.set_ylabel("Y axis")
    ax.set_xlim(-2000, 2000)
    ax.set_ylim(-2000, 2000)
    ax.grid()
    return ax


#  Here we empty the pairInliers and yInliers queue to be able to plot their data latter
def get_inliers(pairInliers, pointsToBePlotted, getPoints):
    while True:
        #print("I'm extracting the data from the pairInliers inside the dedicated thread")
        if getPoints:
            pointsToBePlotted.append(pairInliers.get(True))


#   Calculates the distance between two measures. If the received measure is the stop signal (0),
#   just return a unacceptable distance so the program runs the RANSAC calculation.
def distance_between_measures(new_measure, old_measure):
    if new_measure != 0:
        distance = abs(new_measure[0][3] - old_measure)
    else:
        distance = DISTANCE_LIMIT + 10
    return distance


def scanning(rawPoints, tempPoints, checkEvent, threadEvent, range_finder):
    #range_finder = Lidar('/dev/ttyUSB0')  # initializes serial connection with the lidar
    #arquivo = open('data_test.txt', 'w+')
    #writeFlag = True
    flag = False
    nbr_tours = 0
    nbr_pairs = 0
    nbr_points = 0
    distancesList = []
    QdistancesList = []
    start_time = time.time()
    initial_time = time.time()
    iterator = range_finder.scan('express', max_buf_meas=False, speed=500)  # returns a yield containing each measure
    try:
        for measure in iterator:
            #print("medindo...")
            if time.time() - initial_time > 1:  # Given the time for the Lidar to "heat up"
                if measure[0][3] != 0 and measure[0][3] <= 2000:
                    #if measure[0][0]:
                    #    flag = True
                    dX = measure[0][3] * np.cos(measure[0][2] * ANGLE_TO_RAD + PI/2.)
                    dY = measure[0][3] * np.sin(measure[0][2] * ANGLE_TO_RAD + PI/2.)
                    distancesList.append([dX, dY])
                    QdistancesList.append(QPointF(dX, dY))
                    #if writeFlag:
                    #    arquivo.write("x,y:({} {})".format(dX, dY))
                    nbr_pairs += 1
                    nbr_points += 1
                if measure[0][0] and not threadEvent.is_set() and not checkEvent.is_set():
                    print("Total points number: {}".format(nbr_points))
                    #print("Length of actual list: {}\n".format(len(distancesList)))
                    print("Tempo de um scan: {}".format(time.time()-start_time))
                    start_time = time.time()
                    nbr_tours += 1
                    if len(distancesList) >= 2:
                        rawPoints.append(distancesList[:]) # it contains a list of points inside a list. the first element is a list
                        tempPoints.append(QdistancesList[:])
                        rawPoints.append(0)
                        #writeFlag = False
                        checkEvent.set()
                    time.sleep(0.000001)
                    del distancesList[:]
                    del QdistancesList[:]
                    nbr_pairs = 0
                    nbr_points = 0
                    flag = False
    except (KeyboardInterrupt, SystemExit):
            print("Saindo...")
            range_finder.stop_motor()
            range_finder.reset()
            #rawPoints.put(None)
