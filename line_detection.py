import numpy as np
import os, sys, time
import re
import matplotlib.pyplot as plt
from sklearn import linear_model, datasets


CHUNK_SIZE = 36
PNT_NBR = 50


def get_data(file_name):
    values = []
    try:
        file_descriptor = open(file_name, 'r')
    except IOError:
        print("Could not open file. Exiting...\n")
    else:
        lines = file_descriptor.readlines()
        for line in lines:
            values += re.findall(r"[-+]?\d*\.\d+|\d+", line)  # to collect the numbers inside the string
        file_descriptor.close()
        return [float(item) for item in values]


if __name__ == '__main__':
    xPoints, yPoints = [], []
    i = 0
    data = get_data("./data/scan_prop.txt")
    print(data)
    while i < len(data):
        if data[i] != 0:
            xPoints.append(data[i]*np.cos(np.radians(data[i+1])))
            yPoints.append(data[i]*np.sin(np.radians(data[i+1])))
        i += 2

    #for item in xPoints:
    #    print("valor de x: ", item)
    i = 0
    x = np.array(xPoints)
    y = np.array(yPoints)
    print(y.shape)
    x = x.reshape(-1, 1)
    print(x.shape)
    fig = plt.figure(1)
    ax = fig.add_subplot(111)
    #ax.scatter(xPoints, yPoints, color='blue', s=1)
    finalPointsX = list()
#    finalPointsY = np.array((0, 1), float)

    while i < x.shape[0]:
        print(i)
        if i + PNT_NBR < x.shape[0]:
            k = i + PNT_NBR
        else:
            k = x.shape[0]
        ransac = linear_model.RANSACRegressor(residual_threshold=3)
        ransac.fit(x[i:k], y[i:k])
        inlier_mask = ransac.inlier_mask_
        outlier_mask = np.logical_not(inlier_mask)
        xTemp = np.array(x[i:k])
        print(xTemp.shape)
        yTemp = np.array(y[i:k])
        print("Param: ", ransac.estimator_.coef_)
        print(xTemp[inlier_mask][:, 0])
        line_X = np.arange(xTemp.min(), xTemp.max())[:, np.newaxis]
        line_y_ransac = ransac.predict(line_X)
        plt.plot(line_X, line_y_ransac, color='black', linewidth=2, label='RANSAC regressor')
        ax.scatter(xTemp[inlier_mask], yTemp[inlier_mask], color='green', marker='.', s=1, label='inliers')
        ax.scatter(xTemp[outlier_mask], yTemp[outlier_mask], color='red', marker='.', s=2, label='Outliers')
        i += PNT_NBR
        #plt.pause(0.5)
        finalPointsX.append(xTemp[inlier_mask][:, 0][:])
    print(finalPointsX)
    plt.show()

