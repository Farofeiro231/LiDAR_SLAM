import sys
sys.path.insert(0, '/home/esousacosta/Documents/ECM/E-Gab/LiDAR_SLAM/')
import re
import numpy as np
import matplotlib.pyplot as plt
from find_lmk import *
#from seedSeg import *
from landmarking import *

def file_read(filename):
    fd = open(filename, "r")
    fdW = open("/home/esousacosta/Documents/ECM/E-Gab/LiDAR_SLAM/lmks.txt", "w+")
    lmks = []

    points = re.findall(r"\w+\(([\+\-]?\d+.\d*), ([\+\-]?\d+.\d*)\)[\n,]", fd.read())
#    print(points)
    cloud = np.array([[float(point[0]), float(point[1])] for point in points])
    print(cloud)

    clouds = cloud.T
    x = clouds[0]
    y = clouds[1]

    seeds, lines = lmk_extraction(cloud)
    print(lines)

    i = 0.

    for line in lines:
        lmks.append(Landmark(line[0], line[1], line[2], i*1.0, line[3]))
        i+=1 

    plt.scatter(x, y)

    for seed in seeds:
        seed = seed.T
        plt.scatter(seed[0], seed[1])
    plt.show()

    for lmk in lmks:
        fdW.write("x0:{},y0:{},x1:{},y1:{},s:{},ID:{},xf:{},yf:{}\n".format(lmk.get_orig()[0], lmk.get_orig()[1], lmk.get_dir()[0], lmk.get_dir()[1], lmk.get_size(), lmk.get_id(), lmk.get_end()[0], lmk.get_end()[1]))
    fd.close()
    fdW.close()


file_read("/home/esousacosta/Documents/ECM/E-Gab/LiDAR_SLAM/field.txt")
