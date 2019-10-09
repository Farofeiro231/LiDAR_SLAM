import numpy as np

class Robot():
    
    def __init__(self):
        self.pos = np.array([0., 0., 0.])  # (x, y, theta)
        self.dimX = self.pos.shape[0]
        self.name = "Main robot"

    def get_dim_x(self):
        return self.dimX

    def get_pos(self):
        return self.pos

