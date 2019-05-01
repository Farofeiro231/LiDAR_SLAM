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
        self.pos = np.array[x, y]
        self.timesObserved = 0

    def get_id():
        return self.id

    def get_a():
        return self.a
    
    def get_b():
        return self.b
    
    def get_pos():
        return self.pos

    def observed():
        self.timesObserved += 1

    def decrese_life():
        if self.life > 0:
            self.life -= 1

    def distance_between_origins(landmark):
        distance = np.linalg.norm(self.pos - landmark.get_pos())
        return distance

    def is_equal(landmark):
        distA = abs(self.a - landmark.get_b())
        distB = abs(self.b - landmark.get_b())
        distanceOrigins = self.distance_between_origins(landmarks)
        if distA <= TOLERANCE_A and distB <= TOLERANCE_B and distanceOrigins <= TORELANCE_ORIGINS:
            return True
        else
            return False


