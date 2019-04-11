from tkinter import *
from PyQt5 import QtCore, QtWidgets
import pyqtgraph as pg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from lidar import Lidar
import matplotlib.pyplot as plt
import numpy as np
import time
import ransac_functions
import threading
import multiprocessing as mp


PI = np.pi
DISTANCE_LIMIT = 30  # maximum tolerable distance between two points - in mm - for them to undergo RANSAC
ANGLE_TO_RAD = PI / 180
MIN_NEIGHBOORS = 10  # minimum number of points to even be considered for RANSAC processing


#  Configuring the figure subplots to hold the point cloud plotting. Mode can be rectilinear of polar
def config_plot(figure, lin=1, col=1, pos=1, mode="rectilinear"):
    ax = figure.add_subplot(lin, col, pos, projection=mode)
    ax.set_xlabel("X axis")
    ax.set_ylabel("Y axis")
    ax.grid()
    return ax


#   Here I run the landmark_extraction code inside an indepent process
def ransac_core(my_q, keyFlags, xPoints, yPoints, xInliers, yInliers):
    temp_x, temp_y = 0., 0.
    while True:
        if keyFlags['go'] == True:
            temp_x, temp_y = ransac_functions.landmark_extraction(xPoints, yPoints)
            xInliers.append(temp_x)
            yInliers.append(temp_y)
            #del xPoints[:]
            #del yPoints[:]
            keyFlags['go'] = False

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
    iterator = range_finder.scan('express', max_buf_meas=False, speed=350)  # returns a yield containing each measure
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


def plotting(my_q, keyFlags, theta, distance, xPoints, yPoints, xInliers, yInliers, x, y):

    print("Valor de keyFlags: {}" .format(keyFlags))
    flag = False
    
    root = Tk()
    root.config(background='white')     # configure the root window to contain the plot
    root.geometry("1000x700")

    lab = Label(root, text="Real-time scanning", bg="white", fg="black")
    lab.pack()

    fig = Figure()

    ax = config_plot(fig, col=2, pos=2)#, mode="polar")
    ax1 = config_plot(fig, col=2, pos=1)

    graph = FigureCanvasTkAgg(fig, master=root)
    graph.get_tk_widget().pack(side="top", fill='both', expand=True)

    def plot():
        nonlocal keyFlags
        nonlocal flag
        print("Estou na função tal... Valor de flag: {}" .format(flag))
        measure = 0
        xMask, yMask = 0., 0.
        #theta, distance = list(), list()
        #xPoints, yPoints = list(), list()
        #xInliers, yInliers = list(), list()
        #x, y = list(), list()
        temp_x, temp_y = 0., 0.
        angle, dist = 0., 0.
        neighboors = 0
        tempo = 0.

        
        try:
            while flag:
                tempo = time.time()
                measure = my_q.get(True) # reads from the Queue without blocking
                if measure != 0 and measure[0][3] < 5000:
                    angle = -measure[0][2] * ANGLE_TO_RAD + PI/2.
                    dist = measure[0][3]
                    # Verify if the points are close enough to each other to be ransacked
                    if len(distance) > 0 and distance_between_measures(measure, distance[-1]) <= DISTANCE_LIMIT:
                        xPoints.append(dist * np.cos(angle))
                        yPoints.append(dist * np.sin(angle))
                        neighboors += 1
                    elif neighboors > MIN_NEIGHBOORS:
                        print("Numero de neighboors: {:}" .format(neighboors))
                        #tempo = time.time()
                        #temp_x, temp_y = ransac_functions.landmark_extraction(xPoints, yPoints)
                        #xInliers.append(temp_x)
                        #yInliers.append(temp_y)
                        #del xPoints[:]
                        #del yPoints[:]
                        keyFlags['go'] = True
                        time.sleep(0.1)
                        neighboors = 0
                    else:
                        if not keyFlags['go']:
                            del xPoints[:]
                            del yPoints[:]
                            neighboors = 0 
                    theta.append(angle)
                    distance.append(dist)  # comentar dps daqui pra voltar ao inicial
                    x.append(dist * np.cos(angle))
                    y.append(dist * np.sin(angle))
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
                    tempo = time.time()
                    if neighboors > MIN_NEIGHBOORS:
                        #temp_x, temp_y = ransac_functions.landmark_extraction(xPoints, yPoints)
                        #xInliers.append(temp_x)
                        #yInliers.append(temp_y)
                        #del xPoints[:]
                        #del yPoints[:]
                        keyFlags['go'] = True
                        time.sleep(0.1)
                        neighboors = 0
                    else:
                        if not keyFlags['go']:
                            del xPoints[:]
                            del yPoints[:]
                            neighboors = 0
                    #print("Valor de i:{:}" .format(i))
                    #print("Formato de xInliers:{:}" .format(len(xInliers)))
                    ax.cla()
                    ax.grid()
                    ax1.cla()
                    ax1.grid()
                    theta_array = np.array(theta, dtype="float")
                    distance_array = np.array(distance, dtype="float")
                    #print("Values of xInliers: {}" .format((xInliers[:])))
                    #print("Values of xInliers: {}" .format((yInliers[:])))
                    xMask = np.concatenate(xInliers, axis=0)
                    yMask = np.concatenate(yInliers, axis=0)
                    #print(xMask.shape)
                    ax.scatter(theta_array, distance_array, marker="+", s=3)
                    #ax.scatter(x, y, marker="+", s=3)
                    ax1.scatter(xMask, yMask, marker=".", color='r', s=5)
                    #for i in range(len(xInliers)):
                    #    ax1.plot(xInliers[i], yInliers[i])
                    graph.draw()
                    print("Time to draw the plots: {:.3f}".format(time.time()-tempo))
                    #k = 1
                    #i = 0
                    #del xPoints[:]
                    #del yPoints [:]
                    del x[:]
                    del y[:]
                    del theta[:]
                    del distance[:]
                    del xInliers[:]
                    del yInliers[:]
                print("Time to loop: {:.6f}" .format(time.time() - tempo))
        except KeyboardInterrupt:
            pass

    def run_gui():
        print('beginning')
        nonlocal flag
        flag = not flag
        threading.Thread(target=plot).start()
        #update['value'] = not update['value']

    b = Button(root, text="Start/Stop", command=run_gui(), bg="black", fg="white")
    b.pack()
    
    root.mainloop()
