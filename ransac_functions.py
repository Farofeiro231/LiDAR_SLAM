from skimage.measure import ransac, LineModelND
import threading
import numpy as np
from landmarking import *


THRESHOLD = 10  # maximum distance between a point and the line from the model for inlier classification
MAX_TRIALS = 30
MIN_SAMPLES = 2

#   Function to extract the line represented by the set of points for each subset of rangings. We create an x base array to be able to do << Boolean indexing >>.
def landmark_extraction(pointsToBeFitted, landmarkNumber, landmarks):
    #data =  np.column_stack([pointsToBeFitted[:], yList[:]])  # Inliers returns an array of True or False with inliers as True. 
    data = np.array(pointsToBeFitted)
    del pointsToBeFitted[:]
    model_robust, inliers = ransac(data, LineModelND, min_samples=MIN_SAMPLES, 
                                   residual_threshold=THRESHOLD, max_trials=MAX_TRIALS) 
    params = model_robust.params
    a = params[1][1]/params[1][0]
    b = params[0][1] - a * params[0][0]
    fittedLine = Landmark(a, b, landmarkNumber, params[0][0], params[0][1])
    xBase = np.array(data[inliers, 0])
    if len(landmarks) > 0 and landmarks[-1].is_equal(fittedLine):
        yBase = landmarks[-1].get_a() * xBase + landmarks[-1].get_b()#np.array(data[inliers, 1])
        newLandmark = False
    else:
        yBase = a * xBase + b#np.array(data[inliers, 1])
        newLandmark = True
    #print("--------------------- Finished running RANSAC -----------------")
    return xBase, yBase, fittedLine, newLandmark  #yPredicted


#  Check if the code has set the flag to do the RANSAC or to clear all of the points acquired because there are less of them then the MIN_NEIGHBOORS
def check_ransac(keyFlags, pairInliers, pointsToBeFitted):#, innerFlag):
    temp_x, temp_y = list(), list()
    landmarks = list()
    landmarkNumber = 0
    newLandmark = True
    while True:
        if keyFlags.get(True) and len(pointsToBeFitted) > 2:
            temp_x, temp_y, extractedLandmark, newLandmark = landmark_extraction(pointsToBeFitted, landmarkNumber, landmarks)
            pairInliers.put([temp_x, temp_y])  # Added the coordinates corresponding to the x and y points of the fitted line
            if newLandmark:
                landmarks.append(extractedLandmark)
            print(extractedLandmark)
            landmarkNumber += 1


#   Here I run the landmark_extraction code inside an indepent process
def ransac_core(flags_queue, rawPoints, pairInliers):
    pointsToBeFitted = list()
    temp_x, temp_y = 0., 0.
    ransac_checking = threading.Thread(target=check_ransac, args=(flags_queue, pairInliers, pointsToBeFitted, ))#innerFlag))
    ransac_checking.start()
    try:
        while True:
                pointsToBeFitted.append(rawPoints.get(True))
    except KeyboardInterrupt:
        ransac_checking.join()
        flags_queue.close()
        pass
