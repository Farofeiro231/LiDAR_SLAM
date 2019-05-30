import numpy as np
import matplotlib.pyplot as plt
import re
from skimage.measure import LineModelND
from PyQt5.QtCore import QPointF

SNUM = 6
PMIN = 20
P2L = 30
LMIN = 300
#P2P = 50



fd = open("data_test.txt", "r")
x = []
y = []

temp = re.findall("x,y:\(([+-]?\d+\.\d*) ([+-]?\d+\.\d*)\)", fd.read())
for item in temp:
    x.append(float(item[0]))
    y.append(float(item[1]))


plt.show()


# Here the seeds are expanded to form the landmarks. i is the point the seed begins.
def seed_expansion(lm, x, y, seed, N, i):
    outlier = False
    j = i + SNUM + 1  # gets the next point, because the last seed's point is i + 6
    k = i - 1
    size = 0.
    while not outlier and j < N:
        nextPoint = np.array([[x[j], y[j]]])
        if lm.residuals(nextPoint) < P2L:
            seed = np.concatenate((seed, nextPoint), axis=0) # Inserts the point at the bottom of the current seed. Now we refit the model
            lm.estimate(seed)
            j += 1
        else:
            outlier = True
    #j = j - 1
    outlier = False
    while not outlier and k >= 0:
        previousPoint = np.array([[x[k], y[k]]])
        if lm.residuals(previousPoint) < P2L:
            seed = np.concatenate((previousPoint, seed), axis=0) # Inserts the point at the top of the current seed. Now we refit the model
            lm.estimate(seed)
            k -= 1
        else:
            outlier = True
    k= k + 1
    size = np.linalg.norm(seed[-1] - seed[0])
    if len(seed) > PMIN and size > LMIN:  # Only returns the line and the seed if the final line has a minimum point number greater than PMIN previously set
        #print(lm.params)
        midPoint = int(len(seed[0])/2)
        #if lm.params[1][0]/lm.params[1][1] < 0: # Puts ambiguous
        if lm.params[1][0] < 0:  # Always gets the slope with positive x
                direction = lm.params[1] * -1
                normalizedLM = (seed[midPoint], direction, size)
        else:
            normalizedLM = (seed[midPoint], lm.params[1], size)
        #print("Found line origin, end: {} --- {}".format(seed[0], seed[-1]))
        return normalizedLM, seed, j, k
    else:
        return 0, 0, j, k


#def overlap_correction(lines, seeds, newPoints):
#    N = len(lines)
#    i = 0
#    while i < N - 1:
#        j = i + 1 
#        seeds[0][0] 
#        i++


def lmk_extraction(pointsToBeFitted): 
    #print(pointsToBeFitted[0][:])
    # now we put the points in the proper shape
    newPoints = np.array(pointsToBeFitted[0][:])
    newPoints = newPoints.T
    i = 0
    k = 0
    flag = True
    success = False
    lines = []
    expandedSeeds = []
    sizes = []
    qPointsList = []
    tempLine = 0
    tempSeed = 0
    xSeeds = []
    ySeeds = []

    x = newPoints[0]
    y = newPoints[1]
    #print(x)
    N = len(x)
    #print(N)
    lm = LineModelND()

    while i < N - SNUM:
        #print("Valor de i: {}".format(i))
        flag = True
        seed = np.array([x[i:i+SNUM], y[i:i+SNUM]]).T
        #print(seed)
        success = lm.estimate(seed)
        if success:
            distancesPoint2Line = lm.residuals(seed)
            if not all(dist <= P2L for dist in distancesPoint2Line):
                flag = False
        if flag:  # It means that the seed is valid
            tempLine, tempSeed, i, k = seed_expansion(lm, x, y, seed, N, i)
            if tempLine != 0:
                #print(tempLine.params)
                #print("Inf lim., Sup lim.: [{}, {}]".format(k, i))
                lines.append(tempLine)
                expandedSeeds.append(tempSeed) # adds the germinated seed to the lmk base. Mnx2
        else:
            i += 1 

    #print("\n\n")
    if expandedSeeds != []: 
        #print("OK")
        temp = np.concatenate(expandedSeeds, axis=0)
        temp = temp.T
        xSeeds = temp[0] # Gets all x coordinates for the detected lmks
        ySeeds = temp[1] # Gets all y coordinates for the detected lmks
        qPointsList = [QPointF(xSeeds[i], ySeeds[i]) for i in range(xSeeds.shape[0])]
        return qPointsList, lines
    else:
        return [], []
    


