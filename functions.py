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


def check_ransac(keyFlags, xInliers, yInliers, xList, yList):
    temp_x, temp_y = list(), list()
    while True:
        print("I'm checking for the RANSAC")
        if keyFlags.get(True):
            temp_x, temp_y = ransac_function.landmark_extraction(xList, yList)
            xInliers.put(temp_x)
            yInliers.put(temp_y
        else:
            del xList[:]
            del yList[:]


#   Here I run the landmark_extraction code inside an indepent process
def ransac_core(flags_queue, xPoints, yPoints, xInliers, yInliers):
    xList, yList = list(), list()
    temp_x, temp_y = 0., 0.
    ransac_checking = threading.Thread(target=check_ransac, args=(flags_queue, xInliers, yInliers, xList, yList))
    ransac_checking.start()
    try:
        while True:
            xList.append(xPoints.get(True))
            yList.append(yPoints.get(True))
            print("I'm in the ransac loop")
            #if flags_queue.get(True):
            #    print("Entered the ransac core function...")
            #    temp_x, temp_y = ransac_functions.landmark_extraction(xList, yList)
            #    xInliers.put(temp_x)
            #    yInliers.put(temp_y)
    except KeyboardInterrupt:
        flags_queue.close()
        pass

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





def plotting(my_q):#, keyFlags, theta, distance, xPoints, yPoints, xInliers, yInliers, x, y):
    keyFlags = mp.Queue()
    xPoints, yPoints = mp.Queue(), mp.Queue()
    xInliers, yInliers = mp.Queue(), mp.Queue()
    theta, distance = list(), list()
    x, y = list(), list()
    print("Valor de keyFlags: {}" .format(keyFlags))
    print("Valor de keyFlags: {}" .format(my_q))
    print("Valor de keyFlags: {}" .format(xPoints))
    print("Valor de keyFlags: {}" .format(yPoints))
    flag = False
    
    ransac_process = mp.Process(target=ransac_core, args=(keyFlags, xPoints, yPoints, xInliers, yInliers, ))
    ransac_process.daemon = True  # exits the process as soon as the main program stops
    ransac_process.start()
    print("I haven't yet quite understood the start and join of processes")


    root = Tk()
    root.config(background='white')     # configure the root window to contain the plot
    root.geometry("1000x700")

    lab = Label(root, text="Real-time scanning", bg="white", fg="black")
    lab.pack()

    fig = Figure()

    ax = config_plot(fig, col=1, pos=1, mode='polar')#, mode="polar")
    #ax1 = config_plot(fig, col=2, pos=1)

    graph = FigureCanvasTkAgg(fig, master=root)
    graph.get_tk_widget().pack(side="top", fill='both', expand=True)

    def plot():
        nonlocal keyFlags
        nonlocal flag
        nonlocal theta, distance
        nonlocal xPoints, yPoints
        nonlocal xInliers, yInliers
        nonlocal x, y
        print("Estou na função tal... Valor de flag: {}" .format(flag))
        measure = 0
        xMask, yMask = 0., 0.
        #theta, distance = list(), list()
        #xPoints, yPoints = list(), list()
        #xInliers, yInliers = list(), list()
        #x, y = list(), list()
        temp_x, temp_y = list(), list()
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
                        print("Points added to queue.")
                        xPoints.put(dist * np.cos(angle))
                        yPoints.put(dist * np.sin(angle))
                        #temp_x.append(dist * np.cos(angle))
                        #temp_y.append(dist * np.sin(angle))
                        neighboors += 1
                    elif neighboors > MIN_NEIGHBOORS:
                        #xPoints.put(temp_x[:])
                        #yPoints.put(temp_y[:])
                        keyFlags.put(True)
                        time.sleep(0.001)
                        #del temp_x[:]
                        #del temp_y[:]
                        neighboors = 0
                    else:
                        #    del temp_x[:]
                        #    del temp_y[:]
                            keyFlags.put(False)
                            neighboors = 0 
                    theta.append(angle)
                    distance.append(dist)  # comentar dps daqui pra voltar ao inicial
                    #x.append(dist * np.cos(angle))
                    #y.append(dist * np.sin(angle))
                    print("Length of xInliers: {}" .format(xInliers.empty()))
                elif measure == 0 and len(xInliers) > 1:
                    if neighboors > MIN_NEIGHBOORS:
                        #xPoints.put(temp_x[:])
                        #yPoints.put(temp_y[:])
                        keyFlags.put(True)
                        time.sleep(0.001)
                        #del temp_x[:]
                        #del temp_y[:]
                        neighboors = 0
                    else:
                        #del temp_x[:]
                        #del temp_y[:]
                        keyFlags.put(False)
                        neighboors = 0
                    print("Plotting...")
                    ax.cla()
                    ax.grid()
                    #ax1.cla()
                    #ax1.grid()
                    theta_array = np.array(theta, dtype="float")
                    distance_array = np.array(distance, dtype="float")
                    xMask = np.concatenate(xInliers, axis=0)
                    yMask = np.concatenate(yInliers, axis=0)
                    ax.scatter(theta_array, distance_array, marker="+", s=3)
                    #ax.scatter(x, y, marker="+", s=3)
                    ax1.scatter(xMask, yMask, marker=".", color='r', s=5)
                    graph.draw()
                    #del x[:]
                    #del y[:]
                    del theta[:]
                    del distance[:]
                    del xInliers[:]
                    del yInliers[:]
                #print("Time to loop: {:.6f}" .format(time.time() - tempo))
        except KeyboardInterrupt:
            myThread.join()
            pass
    
    myThread = threading.Thread(target=plot)

    def run_gui():
        print('beginning')
        nonlocal flag
        flag = not flag
        myThread.start()
        #update['value'] = not update['value']

    b = Button(root, text="Start/Stop", command=run_gui(), bg="black", fg="white")
    b.pack()
    
    root.mainloop()
