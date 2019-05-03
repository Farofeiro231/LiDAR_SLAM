import numpy as np
from math import cos, sin, tan, sqrt

R = 50  #  Wheel radius in mm
L = 200   # Robot's base length in mm


def transition_function(xBar, dt, u):  # The shape of u: u = [vl vr].T
    n = x.shape[0]  # The dimension of the state space
    F = np.identity(n)
    B = np.array([R/2.0 * cos( x[2] ), R/2.0 * cos( x[2] )],
                 [R/2.0 * sin( x[2] ), R/2.0 * sin( x[2] )],
                 [-1.0 * R/L, 1.0 * R/L])
    x = np.dot(F, xBar) + dt * np.dot(B, u)
    return x

def transfer_function(x):
    H = np.array([1., 0, 0],
                 [0, 1., 0])
    return np.dot(H, x)

