import numpy as np
import matplotlib.pyplot as plt
import re
from skimage.measure import LineModelND

SNUM = 6
P = 10
P2L = 1
P2P = 50



fd = open("data_test.txt", "r")
x = []
y = []

temp = re.findall("x,y:\(([+-]?\d+\.\d*) ([+-]?\d+\.\d*)\)", fd.read())
for item in temp:
    x.append(float(item[0]))
    y.append(float(item[1]))


plt.show()






if __name__ == "__main__":
    fd = open("data_test.txt", "r")
    x = []
    y = []
    i = 0
    flag = True
    success = False
    
    temp = re.findall("x,y:\(([+-]?\d+\.\d*) ([+-]?\d+\.\d*)\)", fd.read())
    for item in temp:
        x.append(item[0])
        y.append(item[1])
   
    N = len(x)
    lm = LineModelND

    while i < N - SNUM:
        temp = np.array([x[i:i+6],y[i:i+6]]).T
        success = lm.estimate(temp)
        if success:
            distancesPoint2Line = lm.residuals(temp)
            if not all(dist <= P2L for dist in distancesPoint2Line):
                flag = False
                break
        if flag:  # It means that the seed is valid
            

    plt.scatter(x, y)
    plt.show()
    fd.close()


