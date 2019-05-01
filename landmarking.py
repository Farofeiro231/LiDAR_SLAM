import numpy as np

LIFE = 40
TOLERANCE_A = 0.5
TOLERANCE_B = 10
TORELANCE_ORIGINS = 200


class Landmark():
    spec = "line"

    def __init__(self, a, b, ID, x, y):
        self.a = a
        self.b = b
        self.id = ID
        self.life = LIFE
        self.pos = np.array([x, y])
        self.timesObserved = 0

    def __str__(self):
        text = "Landmark ID: {}\n".format(self.id)
        text += "(x, y): ({}, {})\n".format(self.pos[0], self.pos[1]) \
                + "equation: {} * x + {}\n".format(self.a, self.b)
        return text

    def get_id(self):
        return self.id

    def get_a(self):
        return self.a
    
    def get_b(self):
        return self.b
    
    def get_pos(self):
        return self.pos

    def observed(self):
        self.timesObserved += 1

    def decrese_life(self):
        if self.life > 0:
            self.life -= 1

    def distance_between_origins(self, landmark):
        distance = np.linalg.norm(self.pos - landmark.get_pos())
        return distance

    def is_equal(self, landmark):
        distA = abs(self.a - landmark.get_b())
        distB = abs(self.b - landmark.get_b())
        distanceOrigins = self.distance_between_origins(landmarks)
        if distA <= TOLERANCE_A and distB <= TOLERANCE_B and distanceOrigins <= TORELANCE_ORIGINS:
            return True
        else:
            return False


