import numpy as np

SEEN = 50
LIFE = 40
TOLERANCE_A = 0.1
TOLERANCE_B = 50
TOLERANCE = 100


class Landmark():
    spec = "line"

    def __init__(self, a, b, ID, x, y, tipX, tipY):
        self.a = a
        self.b = b
        self.id = ID
        self.life = LIFE
        self.pos = np.array([x, y])
        self.end = np.array([tipX, tipY])
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

    def get_end(self):
        return self.end

    def get_life(self):
        return self.life
    
    def observed(self):
        self.timesObserved += 1
        if self.timesObserved >= SEEN:
            return True
        else:
            return False

    def decrease_life(self):
        if self.life > 0:
            self.life -= 1
        if self.life == 0:
            return True
        else:
            return False

    def reset_life(self):
        self.life = LIFE

    #  This test includes the cases where one landmark in reobserved superposing itself from a former scan
#    def distance_test(self, landmark):
#        theSame = False
#        if self.distance_origin_end(landmark) < TOLERANCE:
#            theSame = True
#        elif self.distance_end_origin(landmark) < TOLERANCE:
#            theSame = True
#        elif self.distance_origin_origin(landmark) < TOLERANCE:
#            theSame = True
#        elif self.distance_end_end(landmark) < TOLERANCE:
#            theSame = True
#        return theSame
#
#    def distance_origin_end(self, landmark):
#        distance = np.linalg.norm(self.pos - landmark.get_end())
#        return distance
#
    def distance_origin_origin(self, landmark):
        distance = np.linalg.norm(self.pos - landmark.get_pos())
        return distance
#    
    def distance_end_end(self, landmark):
        distance = np.linalg.norm(self.end - landmark.get_end())
        return distance
#    
#    def distance_end_origin(self, landmark):
#        distance = np.linalg.norm(self.end - landmark.get_pos())
#        return distance

    def is_equal(self, landmark):
        distA = abs(self.a - landmark.get_a())
        distB = abs(self.b - landmark.get_b())
        #distanceOriginEnd = self.distance_origin_end(landmark)
        #distanceEndOrigin = self.distance_end_origin(landmark)
        if distA <= TOLERANCE_A and distB <= TOLERANCE_B:
            if self.distance_origin_origin(landmark) < TOLERANCE:
            #if distanceOriginEnd <= TOLERANCE or distanceEndOrigin <= TOLERANCE:
                return True
            else:
                return False
        else:
            return False
    
    def ends_equal(self, landmark):
        if self.distance_origin_origin(landmark) < TOLERANCE and self.distance_end_end(landmark) < TOLERANCE:
            #if distanceOriginEnd <= TOLERANCE or distanceEndOrigin <= TOLERANCE:
                return True
        else:
                return False

def landmarks_track(landmarks):
        for landmark in landmarks:
            if landmark.get_life == 0:
                landmarks.remove(landmark)
