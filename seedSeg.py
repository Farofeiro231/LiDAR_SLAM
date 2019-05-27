import numpy as np
import matplotlib.pyplot as plt
import re
from skimage.measure import LineModelND

SNUM = 6
PMIN = 20
P2L = 50
P2P = 50



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
    j = i + 7  # gets the next point, because the last seed's point is i + 6
    k = i - 1
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
    if len(seed) > PMIN:  # Only returns the line and the seed if the final line has a minimum point number greater than PMIN previously set
        return lm, seed, j, k
    else:
        return 0, 0, j, k



if __name__ == "__main__":
    fd = open("data_test.txt", "r")
    x = []
    y = []
    i = 0
    k = 0
    flag = True
    success = False
    lines = []
    expandedSeeds = []
    tempLine = 0
    tempSeed = 0
    
    temp = re.findall("x,y:\(([+-]?\d+\.\d*) ([+-]?\d+\.\d*)\)", fd.read())
    for item in temp:
        x.append(float(item[0]))
        y.append(float(item[1]))
  
    N = len(x)
    print(x[30:37])
    lm = LineModelND()

    while i < N - SNUM:
        print("Valor de i: {}".format(i))
        flag = True
        seed = np.array([x[i:i+SNUM], y[i:i+SNUM]]).T
        print(seed)
        success = lm.estimate(seed)
        if success:
            distancesPoint2Line = lm.residuals(seed)
            if not all(dist <= P2L for dist in distancesPoint2Line):
                flag = False
        if flag:  # It means that the seed is valid
            tempLine, tempSeed, i, k = seed_expansion(lm, x, y, seed, N, i)
            if tempLine != 0:
                print("Inf lim., Sup lim.: [{}, {}]".format(k, i))
                lines.append(tempLine)
                expandedSeeds.append(tempSeed)
        else:
            i += 1
    
    print(expandedSeeds[0].T[0])

    plt.scatter(x, y)
    for lmk in expandedSeeds:
        plt.scatter(lmk.T[0], lmk.T[1])
    plt.show()
    fd.close()


