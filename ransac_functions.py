from skimage.measure import ransac, LineModelND
import threading
import multiprocessing as mp
from landmarking import *
from functions import *
from mainWindow import *

THRESHOLD = 20  # maximum distance between a point and the line from the model for inlier classification
MAX_TRIALS = 10
MIN_SAMPLES = 2

#   Function to extract the line represented by the set of points for each subset of rangings. We create an x base array to be able to do << Boolean indexing >>.
def landmark_extraction(pointsToBeFitted, landmarkNumber, landmarks, landmarkDB):
    i = 0
    equal = False
    deleteLandmark = False
    addToDB = False
    discovering = False
    data = np.array(pointsToBeFitted[0][:])
    #print(data)
    del pointsToBeFitted[:]
    try:
        model_robust, inliers = ransac(data, LineModelND, min_samples=MIN_SAMPLES, 
                                       residual_threshold=THRESHOLD, max_trials=MAX_TRIALS)
    except ValueError:
        print("Couldn't find a fit for the given data")
        return [], [], []
        
    params = model_robust.params
    a = params[1][1]/params[1][0]  # Calculating the coefficients of the line ax + b
    b = params[0][1] - a * params[0][0]
    xBase = np.array(data[inliers, 0])
    tipX = xBase[-1]
    tipY = tipX * a + b
    fittedLine = Landmark(a, b, landmarkNumber, params[0][0], params[0][1], tipX, tipY)  # Creation of a landmark from the previously calculated coefs.
    #  If the landmark is the same as one previously seen, we use the latter to calculate y points.
    if len(landmarks) > 0:# and landmarks[-1].is_equal(fittedLine):
        while i < len(landmarks) and not equal:
            equal = landmarks[i].is_equal(fittedLine)
            #  If the landmark tested is not equal to the new one it means that it has not been seen again; decrease, then, its life. If its life reaches zero, the flag deleteLandmark becomes True and it is removed from the list
            if not equal:
                deleteLandmark = landmarks[i].decrease_life()
                if deleteLandmark:
                    if discovering:  # only needs to remove the landmark from database if it's in the discovery mode
                        if landmarks[i] in landmarkDB:
                            landmarkDB.remove(landmarks[i])
                            print("Excluded landmark: {}".format(landmarks[i]))
                    landmarks.remove(landmarks[i])
            i += 1
        if equal:  # Caso a landmark tenha sido reobservada, sua vida é recuperada
            landmarks[i - 1].reset_life()
            if discovering:  #  if it's the first turn in the field, this flag allows the storage of reference landmarks for further usage
                addToDB = landmarks[i - 1].observed()
                if addToDB and landmarks[i-1] not in landmarkDB:
                    print("Adicionada à DB: {}".format(landmarks[i - 1].get_id()))
                    landmarkDB.append(landmarks[i - 1])
            yBase = landmarks[i - 1].get_a() * xBase + landmarks[i - 1].get_b()#np.array(data[inliers, 1])
            newLandmark = False
        else:
            yBase = a * xBase + b  # np.array(data[inliers, 1])
            newLandmark = True
            #print("Added Landmark! Landmarks: {}".format(len(landmarks)))
    else:
        yBase = a * xBase + b  # np.array(data[inliers, 1])
        newLandmark = True
    qPointsList = [QPointF(xBase[i], yBase[i]) for i in range(xBase.shape[0])]
        #qPointsList.append(tempList) # Passo apenas os pontos em array para a lista final, ao invés de uma lista com um array de pointos

    #print("--------------------- Finished running RANSAC -----------------")
    return qPointsList, fittedLine, newLandmark  #yPredicted


#  Check if the code has set the flag to do the RANSAC or to clear all of the points acquired because there are less of them then the MIN_NEIGHBOORS
def check_ransac(pairInliers, tempPoints, allPoints, pointsToBeFitted, landmarks, threadEvent, checkEvent, landmarkDB):#n, innerFlag):
    inliersList = list()
    #landmarks = list()
    landmarkNumber = 0
    newLandmark = True
    excludedLmks = []
    while True:
        checkEvent.wait()
        #print("Estou na ransac check tread....landmarkDB: {}".format(landmarkDB))
        if pointsToBeFitted != []:
            if pointsToBeFitted[-1] == 0:  # Verifies if the last byte wasn't the plot flag -> 0
                if inliersList != []:
         #          print("Entrei")
         #          print(pointsToBeFitted)
                    del pointsToBeFitted[-1] 
                    tempList, extractedLandmark, newLandmark = landmark_extraction(pointsToBeFitted, landmarkNumber, landmarks, landmarkDB)
                    if tempList != []:
                        inliersList.append(tempList)
                        if newLandmark:
                            landmarks.append(extractedLandmark)
                            #print("Landmarks extraidas: {}".format(len(landmarks)))
                        landmarkNumber += 1
                        pairInliers.append(np.concatenate(inliersList.copy(), axis=0))
                        allPoints.append(np.concatenate(tempPoints.copy(), axis=0))
                        #a = time.time()
                            #print("Passando a bola para plot\n\n\n")
                        #print("Tempo:{:.8f}".format(time.time()-a))
                        threadEvent.set()
                    checkEvent.clear()
                    del inliersList[:]
                    del pointsToBeFitted[:]
                    del tempPoints[:]
                else:  # If the list is empty
                    del pointsToBeFitted[:]
                    checkEvent.clear()
            else:  #if there is no flag indicating a new rotating
                tempList, extractedLandmark, newLandmark = landmark_extraction(pointsToBeFitted, landmarkNumber, landmarks, landmarkDB)
                if tempList != []:
                    inliersList.append(tempList)
                    if newLandmark:
                        landmarks.append(extractedLandmark)
                            #print("Landmarks extraidas: {}".format(len(landmarks)))
                        landmarkNumber += 1                
                checkEvent.clear()


def send_lmks(flagQueue, lmkQueue, lmks):
    flag = 10
    while True:
        flag = flagQueue.get(True)
        if flag == 0:
            lmkQueue.put(lmks.copy())


#   Here I run the landmark_extraction code inside an indepent process
def ransac_core(flagQueue, lmkQueue, rawPoints, range_finder):#, pairInliers):
    discovering = False
    if discovering:
        landmarkFile = open('landmarks.txt', 'w+')
    pairInliers = []
    pointsToBeFitted = []
    allPoints = []
    tempPoints = []
    landmarkDB = []
    landmarks = []
    threadEvent = threading.Event()
    checkEvent = threading.Event()
    scanEvent = threading.Event()
    try:
        ransac_checking = threading.Thread(target=check_ransac, args=(pairInliers, tempPoints, allPoints, pointsToBeFitted, landmarks, threadEvent, checkEvent, landmarkDB))#innerFlag))
        qt_plotting = threading.Thread(target=ploting, args=(pairInliers, allPoints, threadEvent,))
        scan = threading.Thread(target=scanning, args=(pointsToBeFitted, tempPoints, checkEvent, threadEvent, range_finder))
        comm2proc = threading.Thread(target=send_lmks, args=(flagQueue, lmkQueue, landmarks)) 
        ransac_checking.start()
        qt_plotting.start()
        scan.start()
        comm2proc.start()
        scan.join()
        qt_plotting.join()
        comm2proc.join()
    #try:
        #while True:
            #time.sleep(0.000001)  # 0.00001 or 0.000001 are optimal values
            #temp = rawPoints.get(True)
            #pointsToBeFitted.append(temp)
            #if temp != 0:
            #    tempPoints.append([QPointF(point[0], point[1]) for point in temp])
    except KeyboardInterrupt:
        if discovering:
            for lm in landmarkDB:
                landmarkFile.write("a:{},b:{},x0:{},y0:{},x1:{},y1:{}\n".format(lm.get_a(), lm.get_b(), lm.get_pos()[0], lm.get_pos()[1], lm.get_end()[0], lm.get_end()[1]))
        print(landmarkDB)
        #landmarkFile.close()
        del pointsToBeFitted
        del pairInliers
        del tempPoints
        del allPoints
        del landmarks
        del landmarkDB
        print("Saindo do ransac")
        pass
