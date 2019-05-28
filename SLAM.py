import multiprocessing as mp
from functions import *
from ransac_functions import *
from mainWindow import *
from systemClass import *
#keyFlags = {'go': False, 'plot': False}
#x, y = list(), list()
#theta, distance = list(), list()
#rawPoints, yPoints = list(), list()
#xInliers, yInliers = list(), list()

if __name__ == '__main__':
    range_finder = Lidar('/dev/ttyUSB0')
    processes = []
    rawPoints = mp.Queue()
    lmkQueue = mp.Queue()
    flagQueue = mp.Queue()
    #pairInliers = mp.Queue()
    #print("My queue pairInliers: {}".format(pairInliers))
    try:
        #my_queue = mp.Queue()
        #data_acquisition = mp.Process(target=scanning, args=(rawPoints,))
        #data_plotting = mp.Process(target=ploting, args=(pairInliers, ))#keyFlags, theta, distance, rawPoints, yPoints, xInliers, yInliers, x, y, ))
        ransac_process = mp.Process(target=ransac_core, args=(flagQueue, lmkQueue, rawPoints, range_finder))
        system_process = mp.Process(target=simulation, args=(flagQueue, lmkQueue,))
        
        #system_process
        #data_acquisition.start()
        system_process.start()
        ransac_process.start()
        #processes.append(data_plotting)
        processes.append(system_process)
        processes.append(ransac_process)
        for proc in processes:
            proc.join()
    except KeyboardInterrupt:
        #for proc in processes:
        #    proc.terminate()
        range_finder.stop_motor()
        range_finder.reset()
        print("Saindo de tudo")
        exit()
