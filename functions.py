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
MIN_NEIGHBOORS = 80  # minimum number of points to even be considered for RANSAC processing


#  Configuring the figure subplots to hold the point cloud plotting. Mode can be rectilinear of polar
def config_plot(figure, lin=1, col=1, pos=1, mode="rectilinear"):
    ax = figure.add_subplot(lin, col, pos, projection=mode)
    ax.autoscale(False)
    ax.set_xlabel("X axis")
    ax.set_ylabel("Y axis")
    ax.grid()
    return ax


#  Here we empty the pairInliers and yInliers queue to be able to plot their data latter
def get_inliers(pairInliers, pointsToBePlotted, getPoints):
    while True:
        #print("I'm extracting the data from the pairInliers inside the dedicated thread")
        #temp = pairInliers.get(True)
        if getPoints:
            pointsToBePlotted.append(pairInliers.get(True))


#   Calculates the distance between two measures. If the received measure is the stop signal (0),
#   just return a unacceptable distance so the program runs the RANSAC calculation.
def distance_between_measures(new_measure, old_measure):
    if new_measure != 0:
        #print("Nova medida x velha medida: {0:.2f} x {1:.2f}".format(new_measure[0][3], old_measure))
        distance = abs(new_measure[0][3] - old_measure)
    else:
        distance = DISTANCE_LIMIT + 10
    return distance


def scanning(my_q):
    range_finder = Lidar('/dev/ttyUSB0')  # initializes serial connection with the lidar
    nbr_tours = 0
    start_time = time.time()
    iterator = range_finder.scan('express', max_buf_meas=False, speed=300)  # returns a yield containing each measure
    try:
        for measure in iterator:
            #print("medindo...")
            if time.time() - start_time > 1:  # Given the time for the Lidar to "heat up"
                my_q.put(measure)
                if measure[0][0]:
                    nbr_tours += 1
                    my_q.put(0)
    except KeyboardInterrupt:
            #print("Saindo...")
            range_finder.stop_motor()
            range_finder.reset()
            my_q.put(None)



def plotting(my_q, keyFlags, rawPoints, pairInliers):#, keyFlags, theta, distance, rawPoints, yPoints, pairInliers, yInliers, x, y):
    #keyFlags = mp.Queue()
    #rawPoints = mp.Queue()
    #pairInliers, yInliers = mp.Queue(), mp.Queue()
    theta, distance = list(), list()
    pointsToBePlotted = list()
    print("Valor de keyFlags: {}" .format(keyFlags))
    print("Valor de keyFlags: {}" .format(my_q))
    print("Valor de keyFlags: {}" .format(rawPoints))
    flag = False
    getPoints = True
    
    #ransac_process = mp.Process(target=ransac_core, args=(keyFlags, rawPoints, pairInliers, yInliers, ))
    #ransac_process.daemon = True  # exits the process as soon as the main program stops
    #ransac_process.start()

    inliersThread = threading.Thread(target=get_inliers, args=(pairInliers, pointsToBePlotted, getPoints))
    #inliersProcess = mp.Process(target=get_inliers, args=(pairInliers, yInliers, pointsToBePlotted, yPlot, ))
    inliersThread.start()
    #inliersProcess.start()

    root = Tk()
    root.config(background='white')     # configure the root window to contain the plot
    root.geometry("1000x700")

    lab = Label(root, text="Real-time scanning", bg="white", fg="black")
    lab.pack()

    fig = Figure()

    ax = config_plot(fig, col=1, pos=1)#, mode='polar')#, mode="polar")
    #ax1 = config_plot(fig, col=2, pos=2)

    graph = FigureCanvasTkAgg(fig, master=root)
    graph.get_tk_widget().pack(side="top", fill='both', expand=True)

    def plot():
        nonlocal keyFlags
        nonlocal flag
        nonlocal theta, distance
        nonlocal rawPoints
        nonlocal pairInliers
        nonlocal pointsToBePlotted
        nonlocal getPoints
        print("Estou na função tal... Valor de flag: {}" .format(flag))
        measure = 0
        xMask, yMask = 0., 0.
        angle, dist = 0., 0.
        neighboors = 0
        tempo = 0. 
        x, y = list(), list()

        try:
            begin = time.time()
            while flag:
                start = time.time()
                measure = my_q.get(True) # reads from the Queue without blocking
                if measure != 0 and measure[0][3] < 6000 and measure[0][3] > 100:
                    getPoints = True
                    angle = -measure[0][2] * ANGLE_TO_RAD + PI/2.
                    dist = measure[0][3]
                    dX = dist * np.cos(angle)
                    dY = dist * np.sin(angle)
                    # Verify if the points are close enough to each other to be ransacked
                    #if len(distance) > 0 and distance_between_measures(measure, distance[-1]) <= DISTANCE_LIMIT:
                    #    print("valor passado e valor atual: {}, {}".format(distance[-1], measure[0][3]))
                    rawPoints.put([dX, dY])
                        #yPoints.put(dist * np.sin(angle))
                    neighboors += 1
                    if neighboors > MIN_NEIGHBOORS:
                        print("Numero de vizinhos: {}".format(neighboors))
                        keyFlags.put(True)
                        #time.sleep(0.0001)
                        neighboors = 0
                    #else:
                    #    keyFlags.put(False)
                    #    neighboors = 0 
                    theta.append(angle)
                    distance.append(dist)  # comentar dps daqui pra voltar ao inicial
                    x.append(dX)
                    y.append(dY)
                    #print("Is the pointsToBePlotted queue empty: {}" .format(len(pointsToBePlotted)))
                elif measure == 0 and len(pointsToBePlotted) > 0:# and not pairInliers.empty():
                    getPoints = False
                    #if neighboors > MIN_NEIGHBOORS:
                    #    keyFlags.put(True)
                        #time.sleep(0.0001)
                    #    neighboors = 0
                    #else:
                    #    keyFlags.put(False)
                    #    neighboors = 0
                    #print("Plotting...")
                    ax.cla()
                    ax.grid()
                    ax.set_xlim(-2000, 2000)
                    ax.set_ylim(-2000, 2000)
                    ax.autoscale(False) 
                    #ax1.cla()
                    #ax1.grid()
                    #theta_array = np.array(theta, dtype="float")
                    #distance_array = np.array(distance, dtype="float")
                    #mask = np.array( np.concatenate([i[0] for i in pointsToBePlotted], axis=0), np.concatenate([i[1] for i in pointsToBePlotted], axis=0) )
                    xMask = np.concatenate([i[0] for i in pointsToBePlotted], axis=0)  # Gets only the first array of each sub array - only x values for each set of inliers
                    yMask = np.concatenate([i[1] for i in pointsToBePlotted], axis=0)  # Same as above, but for y
                    print("Tamanho de xMask, yMask: {}, {}".format(xMask.shape, yMask.shape))
                    #ax.scatter(theta_array, distance_array, marker="+", s=3)
                    ax.scatter(x, y, marker="+", s=3)
                    ax.scatter(xMask, yMask, marker=".", color='r', s=5)
                    graph.draw()
                    #print("Time to plot without ransac: {:.6f}" .format(time.time() - begin))
                    del x[:]
                    del y[:]
                    del theta[:]
                    del distance[:]
                    del pointsToBePlotted[:]
                    #pairInliers.queue.clear()
                    #yInliers.queue.clear()
                #print("Time to loop: {:.6f}" .format(time.time() - start))
        except KeyboardInterrupt:
            myThread.join()
            inliersThread.join()
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
