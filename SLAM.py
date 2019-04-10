import multiprocessing as mp
import threading
from functions import *

PI = np.pi
DISTANCE_LIMIT = 30  # maximum tolerable distance between two points - in mm - for them to undergo RANSAC
ANGLE_TO_RAD = PI / 180
THRESHOLD = 30  # maximum distance between a point and the line from the model for inlier classification
MAX_TRIALS = 1000
MIN_SAMPLES = 2
MIN_NEIGHBOORS = 10  # minimum number of points to even be considered for RANSAC processing
#   Function to extract the line represented by the set of points for each subset of rangings. We create an x base array to be able to do << Boolean indexing >>.

def landmark_extraction(xPoints, yPoints):
    data =  np.column_stack([xPoints, yPoints])  # Inliers returns an array of True or False with inliers as True.
    model_robust, inliers = ransac(data, LineModelND, min_samples=MIN_SAMPLES, 
                                   residual_threshold=THRESHOLD, max_trials=MAX_TRIALS) 
    xBase = np.array(data[inliers, 0])
    yBase = np.array(data[inliers, 1])
    #yPredicted = model_robust.predict_y(xBase)
    return xBase, yBase  #yPredicted
   
#  Configuring the figure subplots to hold the point cloud plotting. Mode can be rectilinear of polar
def config_plot(figure, lin=1, col=1, pos=1, mode="rectilinear"):
    ax = figure.add_subplot(lin, col, pos, projection=mode)
    ax.set_xlabel("X axis")
    ax.set_ylabel("Y axis")
    ax.grid()
    return ax

#   Calculates the distance between two measures. If the received measure is the stop signal (0),
#   just return a unacceptable distance so the program runs the RANSAC calculation.
def distance_between_measures(new_measure, old_measure):
    if new_measure != 0:
        #print("Nova medida x velha medida: {0:.2f} x {1:.2f}".format(new_measure[0][3], old_measure))
        distance = abs(new_measure[0][3] - old_measure)
        #print("Calculated distance: {:+f}".format(distance))
    else:
        distance = DISTANCE_LIMIT + 10
    return distance


if __name__ == '__main__':
    processes = []
    try:
        my_queue = mp.Queue()
        data_acquisition = mp.Process(target=scanning, args=(my_queue,))
        data_plotting = mp.Process(target=plotting, args=(my_queue,))
        data_acquisition.start()
        data_plotting.start()
        processes.append(data_plotting)
        processes.append(data_acquisition)
    except KeyboardInterrupt:
        for proc in processes:
            proc.join()
        fd.close()
        exit()
