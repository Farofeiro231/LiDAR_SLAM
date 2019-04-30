import multiprocessing as mp
from functions import *
from ransac_functions import *
#keyFlags = {'go': False, 'plot': False}
#x, y = list(), list()
#theta, distance = list(), list()
#rawPoints, yPoints = list(), list()
#xInliers, yInliers = list(), list()


if __name__ == '__main__':
    processes = []
    keyFlags = mp.Queue()
    rawPoints = mp.Queue()
    pairInliers = mp.Queue()
    try:
        my_queue = mp.Queue()
        data_acquisition = mp.Process(target=scanning, args=(my_queue,))
        data_plotting = mp.Process(target=plotting, args=(my_queue, keyFlags, rawPoints, pairInliers, ))#keyFlags, theta, distance, rawPoints, yPoints, xInliers, yInliers, x, y, ))
        ransac_process = mp.Process(target=ransac_core, args=(keyFlags, rawPoints, pairInliers, ))
        data_acquisition.start()
        data_plotting.start()
        ransac_process.start()
        processes.append(data_plotting)
        processes.append(data_acquisition)
        processes.append(ransac_process)
        for proc in processes:
            proc.join()
    except KeyboardInterrupt:
        #for proc in processes:
        #    proc.terminate()
        exit()
