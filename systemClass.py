import numpy as np
from UKFMethods import *
from robot import Robot
from landmarking import *
from filterpy.kalman import UnscentedKalmanFilter as UKF
from filterpy.kalman import MerweScaledSigmaPoints
from math import sqrt, atan2, cos, sin, ceil
import threading
import serial
import time
import re
import sys
import numpy as np

LANDMARK_NUMBER = 1# got replaced by the size of self.landmarks
VAR_DIST = 0.005**2
VAR_ANGLE = 0.003**2
DT = 0.005  # 5 ms
ANGLE_TO_RAD = np.pi/180

class System():
    
    def __init__(self, landmarks):
        self.robot = Robot()
        self.dt = DT
        self.varDist = VAR_DIST
        self.varAngle = VAR_ANGLE
        self.landmarks = landmarks
        self.sigmas = MerweScaledSigmaPoints(n=self.robot.get_dim_x(), alpha=0.0001, beta=2, kappa=0)
        self.ukf = UKF(dim_x=self.robot.get_dim_x(), dim_z=2*len(landmarks), fx=transition_function, hx=transfer_function, dt=self.dt, points=self.sigmas, x_mean_fn=state_mean, z_mean_fn=z_mean, residual_x=residual_x, residual_z=residual_h)
        self.config_ukf()


    def config_ukf(self):
        self.ukf.x = self.robot.get_pos()
        self.ukf.P = np.diag([1., 1., 0.05])#([.1, .1, 0.05])
        self.ukf.R = np.diag([self.varDist, self.varAngle] * len(self.landmarks))
        self.ukf.Q = np.eye(3) * 0.1
        self.angle = 0.

    def simulate_system(self, u):
        self.ukf.predict(u)


def create_lmks_database(lmFD):
    lmParams = re.findall(r"\w+:([\+\-]?\d+.\d*)[\n,]", lmFD.read())
    print(lmParams)
    lmksNbr = ceil(len(lmParams)/5) # Needs to be int for usage in the range method
    params = [float(x) for x in lmParams]  # The original list contains strings
    lmksDB = []
    for i in range(lmksNbr):  # the i is going to number the landmark
        print(i)
        orig = np.array([params[i * 5], params[(i * 5) + 1]])
        direction = np.array([params[(i * 5) + 2], params[(i * 5) + 3]])
        extractedLandmark = Landmark(orig, direction, params[(i * 5) + 4])
        lmksDB.append(extractedLandmark)
    return lmksDB



def lmk_check(lmkQueue, sistema, predictEvent):
    lmkList = []
    tempDB = []
    tempZ = []
    dependableLmks = []
    equal = False
    winner = 0
    match = False
    #tempPos = np.empty([1, 3])
    while True:
        lmkList = lmkQueue.get(True)
        dependableLmks = sistema.landmarks.copy()
        print('{} landmarks recebidas.'.format(len(lmkList)))
        #  Convertion of observed lanmarks into possible equivalents of the database ones. This will give the system the number of scans it should take into account for the update step
        for each in dependableLmks:
            match = False
            distMin = 100000000000000000000000
            winner = []
            print("Landmark in the base: {}".format(each))
            for lmk in lmkList:
                #[x0, y0]
                orig = lmk.get_orig()
                direction = lmk.get_dir()
                [xR, yR, thetaR] = sistema.ukf.x
                thetaR = sistema.angle       
                #thetaR = np.pi/2.

                d0 = sqrt(orig[0]**2 + orig[1]**2)
                theta0 = atan2(orig[1], orig[0])
                #d1 = sqrt(x1**2 + y1**2)
                #theta1 = atan2(y1, x1)
                
                rotM = np.array([[cos(thetaR), -sin(thetaR)], [sin(thetaR), cos(thetaR)]])
                orig = np.dot(rotM, orig)
                direction = np.dot(rotM, direction)
                #end = np.dot(rotM, end)
                #orig = [d0 * cos(normalize_angle(theta0 + thetaR)), d0 * sin(normalize_angle(theta0 + thetaR))]
                #end =  [d1 * cos(normalize_angle(theta1 + thetaR)), d1 * sin(normalize_angle(theta1 + thetaR))]
                orig += np.array([xR, yR])
                #end += [xR, yR]
                #  The tmpLmk is the correspondence of the seen landmark in the ground reference system
                #tmpLmk = Landmark(lmk.get_a(), lmk.get_b(), 0, orig[0], orig[1], end[0], end[1])
                tmpLmk = Landmark(orig, direction, 0)
                print("Tested landmark: {}".format(tmpLmk))
                equal = each.same_update(tmpLmk, TOLERANCE)
                #each.same_decomposed(orig, direction)
                if equal:
                    #dist = np.linalg.norm(each.get_orig() - orig) + np.linalg.norm(each.get_dir() - direction)
                    dist  = each.distance_origin_origin(tmpLmk) + each.distance_dirs(tmpLmk)
                    if dist < distMin:
                        print("Winner: {}".format(tmpLmk))
                        distMin = dist
                        winner = [d0, theta0]
                    #print("Landmark: {}".format(tmpLmk))
                    #print("Landmark observada: {}".format(tmpLmk))
                    #print("Landmark da DB: {}".format(each))
                    if not match:
                        tempDB.append(each)
                        match = True
                    #tempZ.extend([d0, theta0])
                    #dependableLmks.remove(each)
            #if len(tempDB) == len(sistema.landmarks):
            #    break
            if match:
                tempZ.extend(winner)
                dependableLmks.remove(each)
        if tempDB != []:
            #  It is necessary to adapt the size of R for each number of seen landmarks
            print("Dim tempZ, tempDB, system: {}, {}, {}".format(len(tempZ), len(tempDB), len(sistema.landmarks)))
            sistema.ukf.dim_z = 2*len(tempDB)
            sistema.ukf.R = np.diag([sistema.varDist, sistema.varAngle] * len(tempDB))
            sistema.ukf.update(tempZ, landmarks=tempDB)
            print("-----------------Nova posição--------------------\n{}\n{}".format(sistema.ukf.x, sistema.ukf.P))
        else:
            print("No ladnmarks corresponding to the db ones!")
        del tempZ[:]
        del tempDB[:]
        predictEvent.set()


def simulation(flagQueue, lmkQueue):  # This function is going to be used as the core of the UKF process
    try:
        ser = serial.Serial('/dev/ttyACM0', 1000000)
    except:
        print("Couldn't stabilish connection with arduino! Exiting...")
        sys.exit(0)

    lmFD = open('landmarks.txt','r')
    lmksDB = create_lmks_database(lmFD) 
    sistema = System(lmksDB)
    updateEvent = threading.Event()
    predictEvent = threading.Event()
    predictCount = 0
    buff = b''
    index = 0
    vLeft = 0
    vRight = 0
    angle = 0
    u = np.zeros(2)   
    start = time.time()

    updateThread = threading.Thread(target=lmk_check, args=(lmkQueue, sistema, predictEvent))
    updateThread.start()
    predictEvent.set()

    while True:#time.time() - start < :
        predictEvent.wait()
        while b'\x0c' not in buff:
            buff += ser.read(ser.inWaiting())
        
        if buff[0] == 0x40 and len(buff) < 200:  # verification for good flag in the beginning of the message
            #print("Valor de buff:{}".format(buff))
            index = buff.index(b'\xa8')
            index_angle = buff.index(b'\xb9')
            index_end = buff.index(b'\x0c')
            vLeft = float(buff[1:index])#, 10)
            vRight = float(buff[index + 1:index_angle])#, 10)#len(buff) - 1], 10)
            angle = float(buff[index_angle + 1:index_end])#, 10)
            angle = normalize_angle(angle * ANGLE_TO_RAD) 
                #print("Valor de buff {}: {}".format(predictCount, buff))
            buff = buff[index_end + 1:]
        else:
            #print("Wrong format received: {}".format(buff))
            buff = b''

        u[0] = vLeft/60  # Reception of the commands given to the motor (left_speed, right_speed)
        u[1] = vRight/60
        #sistema.ukf.x[2] = angle  # Here the angle got from odometry is fed to the lidar
        sistema.ukf.predict(u=u)
        sistema.angle = angle
        predictCount += 1
        #  If we've done 100 predict steps, we send the flag to the other process asking for the most recent landmarks; only after is the update thread enabled in order to avoid it getting the flag, instead of the other process
        if predictCount >= 10:
            print("Velocities: {}, {}".format(u, angle))
            flagQueue.put(0)
            predictCount = 0
            predictEvent.clear()
            print(sistema.ukf.x)
            print(sistema.ukf.P)
            #print(sistema.ukf.K)

