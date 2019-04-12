import multiprocessing as mp
from functions import *


if __name__ == '__main__':
    manager = mp.Manager()
    processes = []
    #keyFlags = {'go': False, 'plot': False}
    keyFlags = manager.dict()
    keyFlags['go'] = False
    keyFlags['plot'] = False
    print("keyFlags: {}" .format(keyFlags))
    x, y = manager.list(), manager.list()
    theta, distance = manager.list(), manager.list()
    xPoints, yPoints = manager.list(), manager.list()
    xInliers, yInliers = manager.list(), manager.list()
    try:
        my_queue = mp.Queue()
        data_acquisition = mp.Process(target=scanning, args=(my_queue,))
        data_plotting = mp.Process(target=plotting, args=(my_queue, keyFlags, theta, distance, xPoints, yPoints, xInliers, yInliers, x, y, ))
        #ransac_process = mp.Process(target=ransac_core, args=(my_queue, keyFlags, xPoints, yPoints, xInliers, yInliers, ))
        data_acquisition.start()
        data_plotting.start()
        #ransac_process.start()
        processes.append(data_plotting)
        processes.append(data_acquisition)
        #processes.append(ransac_process)
        for proc in processes:
            proc.join()
    except KeyboardInterrupt:
#        for proc in processes:
#            proc.join()
        exit()
