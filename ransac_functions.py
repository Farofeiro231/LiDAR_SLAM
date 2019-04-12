from skimage.measure import ransac, LineModelND
import numpy as np


THRESHOLD = 30  # maximum distance between a point and the line from the model for inlier classification
MAX_TRIALS = 10
MIN_SAMPLES = 2
#   Function to extract the line represented by the set of points for each subset of rangings. We create an x base array to be able to do << Boolean indexing >>.

def landmark_extraction(xPoints, yPoints):
    #print("Tipo de xPoints: {}" .format(type(xPoints[:])))
        #print("Tamanho de yPoints: {}" .format(len(yPoints)))
    #temp_x = xPoints[:].copy()
    #temp_y = yPoints[:].copy()
    #del xPoints[:]
    #del yPoints[:]
    print(xPoints)
    data =  np.column_stack([xPoints[0], yPoints[0]])  # Inliers returns an array of True or False with inliers as True.
    del xPoints[0]
    del yPoints[0]
    #print("Data size of array: {}" .format(data.shape))
    model_robust, inliers = ransac(data, LineModelND, min_samples=MIN_SAMPLES, 
                                   residual_threshold=THRESHOLD, max_trials=MAX_TRIALS) 
    xBase = np.array(data[inliers, 0])
    yBase = np.array(data[inliers, 1])
    #print("--------------------- Finished running RANSAC -----------------")
    #yPredicted = model_robust.predict_y(xBase)
    return xBase, yBase  #yPredicted
