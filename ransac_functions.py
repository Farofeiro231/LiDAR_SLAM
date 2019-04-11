from skimage.measure import ransac, LineModelND
import numpy as np


THRESHOLD = 30  # maximum distance between a point and the line from the model for inlier classification
MAX_TRIALS = 1000
MIN_SAMPLES = 2
#   Function to extract the line represented by the set of points for each subset of rangings. We create an x base array to be able to do << Boolean indexing >>.

def landmark_extraction(xPoints, yPoints):
    while True:
        print("Tamanho de xPoints: {}" .format(len(xPoints)))
        print("Tamanho de yPoints: {}" .format(len(yPoints)))
    data =  np.column_stack([xPoints, yPoints])  # Inliers returns an array of True or False with inliers as True.
    print(data)
    model_robust, inliers = ransac(data, LineModelND, min_samples=MIN_SAMPLES, 
                                   residual_threshold=THRESHOLD, max_trials=MAX_TRIALS) 
    xBase = np.array(data[inliers, 0])
    yBase = np.array(data[inliers, 1])
    #yPredicted = model_robust.predict_y(xBase)
    return xBase, yBase  #yPredicted
