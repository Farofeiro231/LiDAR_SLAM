import multiprocessing as mp
from functions import *


if __name__ == '__main__':
    manager = mp.Manager()
    processes = []
    #keyFlags = {'go': False, 'plot': False}
    keyFlags = manager.dict()
    keyFlags['go'] = False
    keyFlags['plot'] = False
    x, y = list(), list()
    theta, distance = list(), list()
    xPoints, yPoints = list(), list()
    xInliers, yInliers = list(), list()
    try:
        my_queue = mp.Queue()
        data_acquisition = mp.Process(target=scanning, args=(my_queue,))
        data_plotting = mp.Process(target=plotting, args=(my_queue, keyFlags, theta, distance, xPoints, yPoints, xInliers, yInliers, x, y, ))
        ransac_process = mp.Process(target=ransac_core, args=(my_queue, keyFlags, xPoints, yPoints, xInliers, yInliers, ))
        data_acquisition.start()
        ransac_process.start()
        data_plotting.start()
        processes.append(data_plotting)
        processes.append(data_acquisition)
        processes.append(ransac_process)
    except KeyboardInterrupt:
        for proc in processes:
            proc.join()
        fd.close()
        exit()
