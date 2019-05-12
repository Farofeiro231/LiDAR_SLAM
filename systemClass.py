import numpy as np
import UKFMethods
import robot
import filterpy.kalman import UnscentedKalmanFilter as UKF
import filterpy.kalman import MerweScaledSigmaPoints
import serial
import time

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



def simulation():
    ser = serial.Serial('dev/ttyUSB1', 9600)
    dataBytes = 0
    while True:
        while dataBytes == 0:
            dataBytes = ser.inWaiting()
            time.sleep(0.0001)
        ser.read(dataBytes)

