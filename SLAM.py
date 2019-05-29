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
        ransac_process = mp.Process(target=ransac_core, args=(flagQueue, lmkQueue, rawPoints, range_finder))
        #system_process = mp.Process(target=simulation, args=(flagQueue, lmkQueue,))
        #system_process.start()
        ransac_process.start()
        #processes.append(system_process)
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
