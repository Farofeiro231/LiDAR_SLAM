from skimage.measure import ransac, LineModelND
import threading
import numpy as np


THRESHOLD = 50  # maximum distance between a point and the line from the model for inlier classification
MAX_TRIALS = 10
MIN_SAMPLES = 2

#   Function to extract the line represented by the set of points for each subset of rangings. We create an x base array to be able to do << Boolean indexing >>.
def landmark_extraction(xList):#, yList, innerFlag):
    #data =  np.column_stack([xList[:], yList[:]])  # Inliers returns an array of True or False with inliers as True.
    #innerFlag[0] = False
    data = np.array(xList)
    del xList[:]
    #del yList[:]
    model_robust, inliers = ransac(data, LineModelND, min_samples=MIN_SAMPLES, 
                                   residual_threshold=THRESHOLD, max_trials=MAX_TRIALS) 
    params = model_robust.params
    print(params)
    #with params[0][1] as coefs:
    a = params[1][1]/params[1][0]
    #with params[0][0] as origin:
    b = params[0][1] - a * params[0][0]
    print("Valores de a e b: {:.2f} {:.2f}" .format(a, b))
    xBase = np.array(data[inliers, 0])
    yBase = a * xBase + b#np.array(data[inliers, 1])
    #print("--------------------- Finished running RANSAC -----------------")
    return xBase, yBase  #yPredicted


#  Check if the code has set the flag to do the RANSAC or to clear all of the points acquired because there are less of them then the MIN_NEIGHBOORS
def check_ransac(keyFlags, xInliers, yInliers, xList):#, innerFlag):
    temp_x, temp_y = list(), list()
    while True:
        #print("I'm checking for the RANSAC")
        if keyFlags.get(True) and len(xList) > 2:
            temp_x, temp_y = landmark_extraction(xList)#, yList, innerFlag)
            xInliers.put(temp_x)
            yInliers.put(temp_y)
        else:
            del xList[:]


#   Here I run the landmark_extraction code inside an indepent process
def ransac_core(flags_queue, xPoints, xInliers, yInliers):
    xList = list()
    temp_x, temp_y = 0., 0.
    ransac_checking = threading.Thread(target=check_ransac, args=(flags_queue, xInliers, yInliers, xList, ))#innerFlag))
    ransac_checking.start()
    try:
        while True:
                xList.append(xPoints.get(True))
    except KeyboardInterrupt:
        flags_queue.close()
        pass
