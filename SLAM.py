import multiprocessing as mp
from tkinter import *
from PyQt5 import QtCore, QtWidgets
import pyqtgraph as pg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
from lidar import Lidar
import matplotlib.pyplot as plt
import numpy as np
import time
from skimage.measure import ransac, LineModelND

PI = np.pi
DISTANCE_LIMIT = 40  # maximum tolerable distance between two points - in mm - for them to undergo RANSAC
PNT_NBR = 10
ANGLE_TO_RAD = PI / 180
THRESHOLD = 1
MAX_TRIALS = 100
MIN_SAMPLES = 2
#   Function to extract the line represented by the set of points for each subset of rangings. We create an x base array to be able to do << Boolean indexing >>.

def landmark_extraction(xPoints, yPoints):
    data =  np.column_stack([xPoints, yPoints])  # Inliers returns an array of True or False with inliers as True.
    model_robust, inliers = ransac(data, LineModelND, min_samples=MIN_SAMPLES, 
                                   residual_threshold=THRESHOLD, max_trials=MAX_TRIALS) 
    xBase = np.array(data[inliers, 0])
    yPredicted = model_robust.predict_y(xBase)
    return xBase, yPredicted
   
#  Configuring the figure subplots to hold the point cloud plotting. Mode can be rectilinear of polar
def config_plot(figure, lin=1, col=2, pos=1, mode="rectilinear"):
    ax = figure.add_subplot(lin, col, pos, projection=mode)
    ax.set_xlabel("X axis")
    ax.set_ylabel("Y axis")
    ax.grid()
    return ax

#   Calculates the distance between two measures. If the received measure is the stop signal (0),
#   just return a unacceptable distance so the program runs the RANSAC calculation.
def distance_between_measures(new_measure, old_measure):
    if new_measure != 0:
        #print("Nova medida x velha medida: {0:.2f} x {1:.2f}".format(new_measure[0][3], old_measure))
        distance = abs(new_measure[0][3] - old_measure)
        #print("Calculated distance: {:+f}".format(distance))
    else:
        distance = DISTANCE_LIMIT + 10
    return distance

def scanning(my_q):
    range_finder = Lidar('/dev/ttyUSB0')  # initializes serial connection with the lidar
    nbr_tours = 0
    start_time = time.time()
    iterator = range_finder.scan('express', max_buf_meas=False, speed=450)  # returns a yield containing each measure
    try:
        for measure in iterator:
            #print("medindo...")
            if time.time() - start_time > 2:  # Given the time for the Lidar to "heat up"
                my_q.put(measure)
                if measure[0][0]:
                    nbr_tours += 1
                    my_q.put(0)
    except KeyboardInterrupt:
            #print("Saindo...")
            range_finder.stop_motor()
            range_finder.reset()
            my_q.put(None)


def plotting(my_q):

    update = {'value': True}
    flag = True

    root = Tk()
    root.config(background='white')     # configure the root window to contain the plot
    root.geometry("1000x700")

    lab = Label(root, text="Real-time scanning", bg="white", fg="black")
    lab.pack()

    fig = Figure()

    ax = config_plot(fig, pos=1, mode="polar")
    ax1 = config_plot(fig, pos=2)

    graph = FigureCanvasTkAgg(fig, master=root)
    graph.get_tk_widget().pack(side="top", fill='both', expand=True)



    def plot():
        nonlocal flag
        measure = 0
        xMask, yMask = 0., 0.
        theta, distance = list(), list()
        xPoints, yPoints = list(), list()
        xInliers, yInliers = list(), list()
        temp_x, temp_y = 0., 0.
        angle, dist = 0., 0.
        neighboors = 0
        i = 0
        k = 1
        trained = False
        try:
            while flag:
                measure = my_q.get(True) # reads from the Queue without blocking
                if measure != 0 and measure[0][3] < 5000:
                    angle = -measure[0][2] * ANGLE_TO_RAD + PI/2.
                    dist = measure[0][3]
                    # Verify if the points are close enough to each other to be ransacked
                    if len(distance) > 0 and distance_between_measures(measure, distance[-1]) <= DISTANCE_LIMIT:
                        xPoints.append(dist * np.cos(angle))
                        yPoints.append(dist * np.sin(angle))
                        neighboors += 1
                    elif neighboors > 4:
                        temp_x, temp_y = landmark_extraction(xPoints, yPoints)
                        xInliers.append(temp_x)
                        yInliers.append(temp_y)
                        del xPoints[:]
                        del yPoints[:]
                        neighboors = 0
                    else:
                        del xPoints[:]
                        del yPoints[:]
                        neighboors = 0 
                    theta.append(angle)
                    distance.append(dist)  # comentar dps daqui pra voltar ao inicial
                    #xPoints.append(dist*np.cos(angle))
                    #yPoints.append(dist*np.sin(angle))
                    #if i >= k * PNT_NBR:
                        #print("Entrei! Valor de i e k: {:}, {:}" .format(i, k))
                    #    temp_x, temp_y = landmark_extraction(xPoints[(k - 1) * PNT_NBR : i ], yPoints[ (k - 1) * PNT_NBR : i])
                    #    xInliers.append(temp_x)
                    #    yInliers.append(temp_y)
                    #    k += 1
                    #i += 1
                elif measure == 0 and len(xInliers) > 1:
                    if neighboors > 4:
                        temp_x, temp_y = landmark_extraction(xPoints, yPoints)
                        xInliers.append(temp_x)
                        yInliers.append(temp_y)
                        del xPoints[:]
                        del yPoints[:]
                        neighboors = 0
                    else:
                        del xPoints[:]
                        del yPoints[:]
                        neighboors = 0
                    print("Desenhando...\n")
                    #print("Valor de i:{:}" .format(i))
                    #print("Formato de xInliers:{:}" .format(len(xInliers)))
                    ax.cla()
                    ax.grid()
                    ax1.cla()
                    ax1.grid()
                    theta_array = np.array(theta, dtype="float")
                    distance_array = np.array(distance, dtype="float")
                    xMask = np.concatenate(xInliers, axis=0)
                    yMask = np.concatenate(yInliers, axis=0)
                    #print(xMask.shape)
                    ax.scatter(theta_array, distance_array, marker="+", s=3)
                    ax1.scatter(xMask, yMask, marker=".", color='r', s=5)
                    #for i in range(len(xInliers)):
                    #    ax1.plot(xInliers[i], yInliers[i])
                    graph.draw()
                    #k = 1
                    #i = 0
                    #del xPoints[:]
                   # del yPoints [:]
                    del theta[:]
                    del distance[:]
                    del xInliers[:]
                    del yInliers[:]
        except KeyboardInterrupt:
            pass

    def run_gui():
        print('beginning')
        threading.Thread(target=plot).start()
        #nonlocal flag
        #flag = not flag
        #update['value'] = not update['value']

    b = Button(root, text="Start/Stop", command=run_gui(), bg="black", fg="white")
    b.pack()

    root.mainloop()


if __name__ == '__main__':
    processes = []
    try:
        my_queue = mp.Queue()
        data_acquisition = mp.Process(target=scanning, args=(my_queue,))
        data_acquisition.start()
        data_plotting = mp.Process(target=plotting, args=(my_queue,))
        data_plotting.start()
        processes.append(data_plotting)
        processes.append(data_acquisition)
    except KeyboardInterrupt:
        for proc in processes:
            proc.join()
        fd.close()
        exit()
