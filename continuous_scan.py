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


def scanning(my_q):
    range_finder = Lidar('/dev/ttyUSB1')  # initializes serial connection with the lidar
    nbr_tours = 0
    start_time = time.time()
    iterator = range_finder.scan('express', max_buf_meas=False, speed=350)  # returns a yield containing each measure
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


def plotting(my_q):

    update = {'value': True}
    flag = True

    root = Tk()
    root.config(background='white')     # configure the root window to contain the plot
    root.geometry("1000x700")

    lab = Label(root, text="Real-time scanning", bg="white", fg="black")
    lab.pack()

    fig = Figure()

    ax = fig.add_subplot(111, projection="polar")
    ax.set_xlabel("X axis")
    ax.set_ylabel("Y axis")
    ax.grid()

    graph = FigureCanvasTkAgg(fig, master=root)
    graph.get_tk_widget().pack(side="top", fill='both', expand=True)

    def plot():
        nonlocal flag
        tempo = 0.
        measure = list()
        theta, distance = list(), list()
        try:
            while flag:
                tempo = time.time()
                measure = my_q.get(True)  # reads from the Queue without blocking
                if measure != 0 and measure[0][3] < 5000:
                    theta.append(-measure[0][2]*np.pi/180+np.pi/2)
                    distance.append(measure[0][3])
                elif measure == 0:
                    tempo = time.time()
                    ax.cla()
                    ax.grid()
                    #for medida in measure:
                     #   if medida != 0 and medida[0][3] < 1000:
                     #       fd.write("Distance: %s Angle: %s\n" % (medida[0][3], medida[0][2]))
                     #       theta.append(-medida[0][2]*np.pi/180+np.pi/2)
                     #       distance.append(medida[0][3])
                    theta_array = np.array(theta, dtype="float")
                    distance_array = np.array(distance, dtype="float")
                    del theta[:]
                    del distance[:]
                    ax.scatter(theta_array, distance_array, marker="+", s=3)
                    graph.draw()
                    print("Time to plot: {:.3f}".format(time.time() - tempo))
                    #fd.write("\n\n")
                print("Loop process time: {:.6f}" .format(time.time() - tempo))
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
        fd = open("scanning_data.txt", "w+")
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
