import numpy as np
from UKFMethods import *
from robot import Robot
from landmarking import Landmark
from filterpy.kalman import UnscentedKalmanFilter as UKF
from filterpy.kalman import MerweScaledSigmaPoints
from math import sqrt, atan2, cos, sin
import threading
import serial
import time
import re
import sys

LANDMARK_NUMBER = 1# got replaced by the size of self.landmarks
VAR_DIST = 0.5**2
VAR_ANGLE = 0.3**2
DT = 0.005  # 5 ms

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
        self.ukf.Q = np.eye(3) * 0.001

    def simulate_system(self, u):
        self.ukf.predict(u)


def create_lmks_database(lmFD):
    lmParams = re.findall(r"\w+:([\+\-]?\d+.\d*)[\n,]", lmFD.read())
    lmksNbr = int(len(lmParams)/6) # Needs to be int for usage in the range method
    params = [float(x) for x in lmParams]  # The original list contains strings
    lmksDB = []
    for i in range(lmksNbr):  # the i is going to number the landmark
        extractedLandmark = Landmark(params[i * 6], params[(i * 6) + 1]
                            , i, params[(i * 6) + 2], params[(i * 6) + 3]
                            , params[(i * 6) + 4], params[(i * 6) + 5])
        lmksDB.append(extractedLandmark)
    return lmksDB



def lmk_check(lmkQueue, sistema, predictEvent):
    lmkList = []
    tempDB = []
    tempZ = []
    equal = False
    #tempPos = np.empty([1, 3])
    while True:
        lmkList = lmkQueue.get(True)
        print('recebido!')
        #  Convertion of observed lanmarks into possible equivalents of the database ones. This will give the system the number of scans it should take into account for the update step
        for lmk in lmkList:
            [x0, y0] = lmk.get_pos()
            [x1, y1] = lmk.get_end()
            [xR, yR, thetaR] = sistema.ukf.x
            d0 = sqrt(x0**2 + y0**2)
            theta0 = atan2(y0, x0)
            d1 = sqrt(x1**2 + y1**2)
            theta1 = atan2(y1, x1)
            orig = [d0 * cos(normalize_angle(theta0 + thetaR)), d0 * sin(normalize_angle(theta0 + thetaR))]
            end =  [d1 * cos(normalize_angle(theta1 + thetaR)), d1 * sin(normalize_angle(theta1 + thetaR))]
            orig += [xR, yR]
            end += [xR, yR]
            #  The tmpLmk is the correspondence of the seen landmark in the ground reference system
            tmpLmk = Landmark(lmk.get_a(), lmk.get_b(), 0, orig[0], orig[1], end[0], end[1])
            for each in sistema.landmarks:
                equal = (tmpLmk.is_equal(each))
                if equal:
                    tempDB.append(each)
                    tempZ.extend([d0, theta0])
        if tempZ != []:
            print("Dim tempZ, tempDB: {}, {}".format(len(tempZ), len(tempDB)))
            sistema.ukf.dim_z = 2*len(tempDB)
            sistema.ukf.R = np.diag([sistema.varDist, sistema.varAngle] * len(tempDB))
            sistema.ukf.update(tempZ, landmarks=tempDB)
        else:
            print("No ladnmarks corresponding to the db ones!")
        predictEvent.set()

def simulation(flagQueue, lmkQueue):  # This function is going to be used as the core of the UKF process
    try:
        ser = serial.Serial('/dev/ttyACM0', 115200)
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
    u = np.zeros(2)   
    start = time.time()

    updateThread = threading.Thread(target=lmk_check, args=(lmkQueue, sistema, predictEvent))
    updateThread.start()
    predictEvent.set()

    while time.time() - start < 10:
        predictEvent.wait()
        while b'\x0c' not in buff:
            buff += ser.read(ser.inWaiting())
        
        if buff[0] == 0x40 and len(buff) < 20:  # verification for good flag in the beginning of the message
            index = buff.index(b'\xa8')
            vLeft = int(buff[1:index], 10)
            vRight = int(buff[index + 1:len(buff) - 1], 10)
            print("Valor de buff {}: {}".format(predictCount, buff))
            buff = b''
        else:
            print("Wrong format received: {}".format(buff))
            buff = b''

        u[0] = vLeft  # Reception of the commands given to the motor (left_speed, right_speed)
        u[1] = vRight
        print("Velocities: {}".format(u))
        sistema.ukf.predict(u=u)
        print("Morre diabo")
        predictCount += 1
        #  If we've done 100 predict steps, we send the flag to the other process asking for the most recent landmarks; only after is the update thread enabled in order to avoid it getting the flag, instead of the other process
        if predictCount >= 10:
            flagQueue.put(0)
            predictCount = 0
            predictEvent.clear()
            print(sistema.ukf.x)
            print(sistema.ukf.P)

