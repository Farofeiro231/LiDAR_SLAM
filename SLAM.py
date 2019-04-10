import multiprocessing as mp
from functions import *


if __name__ == '__main__':
    processes = []
    x, y = list(), list()
    theta, distance = list(), list()
    xPoints, yPoints = list(), list()
    xInliers, yInliers = list(), list()
    try:
        my_queue = mp.Queue()
        data_acquisition = mp.Process(target=scanning, args=(my_queue,))
        data_plotting = mp.Process(target=plotting, args=(my_queue, theta, distance, xPoints, yPoints, xInliers, yInliers, x, y, ))
        data_acquisition.start()
        data_plotting.start()
        processes.append(data_plotting)
        processes.append(data_acquisition)
    except KeyboardInterrupt:
        for proc in processes:
            proc.join()
        fd.close()
        exit()
