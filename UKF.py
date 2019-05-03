import numpy as np
from math import cos, sin, tan, sqrt, atan2

R = 50  #  Wheel radius in mm
L = 200   # Robot's base length in mm

def normalize_angle(angle):
    angle = angle % (2 * np.pi)
    if angle > np.pi:
        angle -= 2 * np.pi
    return angle



def transition_function(x, dt, u):  # The shape of u: u = [vl vr].T
    n = x.shape[0]  # The dimension of the state space
    fx = np.identity(n)
    bx = np.array([R/2.0 * cos( x[2] ), R/2.0 * cos( x[2] )],
                 [R/2.0 * sin( x[2] ), R/2.0 * sin( x[2] )],
                 [-1.0 * R/L, 1.0 * R/L])
    xBar = np.dot(fx, x) + dt * np.dot(bx, u)
    return xBar

def transfer_function(x, landmarks):
    hx = []  #  Array to keep the pairs: distance, angle, to all given landmarks
    # the extend command is useful to append items to a list individually instead of in array form
    for lndmrk in landmarks:
        (px, py) = lndmrk.get_pos()[0], lndmrk.get_pos()[1]
        dist = sqrt((px - x[0])**2 + (py - x[1])**2)  # Calculates distance from the robot to the landmark
        angle = atan2(py - x[1]) # Calculates the angle between the robot and the landmark
        hx.extend([dist, ])
    H = np.array([1., 0, 0],
                 [0, 1., 0])
    return np.dot(H, x)

