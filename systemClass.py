import numpy as np
import UKFMethods
import robot
import landmarking
import filterpy.kalman import UnscentedKalmanFilter as UKF
import filterpy.kalman import MerweScaledSigmaPoints
import serial
import time
import re
import sys

LANDMARK_NUMBER = 8 # got replaced by the size of self.landmarks
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
        self.ukf = UKF(dim_x=self.robot.get_dim_x(), dim_z=2*len(landmarks), fx=transition_function, hx=transfer_function, dt=dt, points=self.sigmas, x_mean_fn=state_mean, z_mean_fn=z_mean, residual_x=residual_x, residual_z=residual_h)
        self.config_ukf()


    def config_ukf(self):
        self.ukf.x = self.robot.get_pos()
        self.ukf.P = np.diag([.1, .1, 0.05])
        self.ukf.R = np.diag([self.varDist, self.varAngle] * LANDMARK_NUMBER)
        self.ukf.Q = np.eye(3) * 0.001

    def simulate_system(self, u):
        self.ukf.predict(u)


def create_lmks_database(lmFD):
    lmParams = re.findall(r"\w+:([\+\-]?\d+.\d*)[\n,]", lmFD.read())
    lmksNbr = len(lmParams)/6.0
    params = [float(x) for x in lmParams]  # The original list contains strings
    lmksDB = []
    for i in range(lmksNbr):  # the i is going to number the landmark
        extractedLandmark = Landmark(params[i * 6], params[(i * 6) + 1]
                            , i, params[(i * 6) + 2], params[(i * 6) + 3]
                            , params[(i * 6) + 4], params[(i * 6) + 5])
        lmksDB.append(extractedLandmark)
    return lmksDB



def simulation():  # This function is going to be used as the core of the UKF process
    try:
        ser = serial.Serial('dev/ttyACM0', 115200)
    except:
        print("Couldn't stabilish connection with arduino! Exiting...")
        sys_exit(0)

    lmFD = open('landmarks.txt','r')
    lmksDB = create_lmks_database(lmFD) 
    sistema = System(lmksDB)
    nbr_predict = 0
    buff = b''
    index = 0
    vLeft = 0
    vRight = 0
    u = np.zeros(2)
    
    start = time.time()
    while time.time() - start < 10:
        while b'\x0c' not in buff:
            buff += ser.read(ser.inWaiting())
        
        if buf[0] = 0x40:  # verification for good flag in the beginning of the message
            index = buff.index(b'\xa8')
            vLeft = int(buf[1:index], 10)
            vRight = int(buf[index + 1:len(buf) - 1], 10)
            buff = b''
        else:
            print("Wrong format received: {}".format(buff))
            buff = b''

        u[0] = vLeft  # Reception of the commands given to the motor (left_speed, right_speed)
        u[1] = vRight
        sistema.ukf.predict(u)
        


