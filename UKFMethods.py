import numpy as np
from math import cos, sin, tan, sqrt, atan2
from filterpy.kalman import UnscentedKalmanFilter as UKF
from filterpy.kalman import MerweScaledSigmaPoints

R = 50  #  Wheel radius in mm
L = 200   # Robot's base length in mm
#dt = 0.005  # 5 ms

def normalize_angle(angle):
    angle = angle % (2 * np.pi)
    if angle > np.pi:
        angle -= 2 * np.pi
    return angle


def transition_function(x, dt, u, angle):  # The shape of u: u = [vl vr].T
    #n = x.shape[0]  # The dimension of the state space
    #fx = np.identity(n)
    #bx = np.array([[R/2.0 * cos( x[2] ), R/2.0 * cos( x[2] )],
                 [R/2.0 * sin( x[2] ), R/2.0 * sin( x[2] )],
                 [-1.0 * R/L, 1.0 * R/L]])
    #xBar = np.dot(fx, x) + dt * np.dot(bx, u)
    xBar = np.array([u, angle])
    return xBar

def transfer_function(x, landmarks):
    hx = []  #  Array to keep the pairs: distance, angle, to all given landmarks
    # the extend command is useful to append items to a list individually instead of in array form
    for lndmrk in landmarks:
        pos = lndmrk.get_pos()
        px, py = pos[0], pos[1]
        dist = sqrt((px - x[0])**2 + (py - x[1])**2)  # Calculates distance from the robot to the landmark
        angle = atan2(py - x[1], px - x[0]) # Calculates the angle between the robot and the landmark
        hx.extend([dist, normalize_angle(angle - x[2])])
    return np.array(hx)


def state_mean(sigmas, Wm):  # Sigmas is of the form M(2n+1)xn
    x = np.zeros(3)
    sum_sin = np.sum(sin(np.dot(sigmas[:, 2], Wm)))#np.dot(sin(np.dot(sigmas[:, 2], Wm)))) 
    sum_cos = np.sum(cos(np.dot(sigmas[:, 2], Wm)))
    x[0] = np.sum(np.dot(sigmas[:, 0], Wm))
    x[1] = np.sum(np.dot(sigmas[:, 1], Wm))
    x[2] = atan2(sum_sin, sum_cos)
    return x

def z_mean(sigmas, Wm):
    nbrLmkrs = sigmas.shape[1]  # number of landmarks
    x = np.zeros(nbrLmkrs)

    for z in range(0, nbrLmkrs, 2):
        sum_sin = np.sum(sin(np.dot(sigmas[:, z+1], Wm)))  # Wm is a column vector
        sum_cos = np.sum(cos(np.dot(sigmas[:, z+1], Wm)))

        x[z] = np.sum(np.dot(sigmas[:, z], Wm))
        x[z+1] = atan2(sum_sin, sum_cos)
    return x        #  this x is actually u_z, in the format [dist0, angle0, dist1, angle1, ..., distk, anglek], avec k = nbrLmkrs


def residual_x(a, b):
    x = a - b
    x[2] = normalize_angle(x[2])
    return x


def residual_h(a, b):
    y = a - b
    #  data in format [dist_0, angle_0, dist_2, angle_2]
    for i in range(0, len(y), 2):
        y[i+1] = normalize_angle(y[i+1])
    return y


















