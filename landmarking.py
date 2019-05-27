import numpy as np

SEEN = 50
LIFE = 40
TOLERANCE_A = 0.1
TOLERANCE_B = 50
TOLERANCE = 200


class Landmark():
    spec = "line"

    def __init__(self, lm, ID):
        self.orig = lm[0]
        self.dir = lm[1]
        self.id = ID
        self.life = LIFE
        self.timesObserved = 0
        self.observed = False

    def __str__(self):
        text = "Landmark ID: {}\n".format(self.id)
        text += "(x, y): ({}, {})\n".format(self.orig[0], self.orig[1]) \
                + "direction: {}, {}\n".format(self.dir[0], self.dir[1])
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

    def get_observed(self):
        return self.observed
    
    def observed(self):
        self.timesObserved += 1
        self.observed = True
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
    removed = [] 
    for landmark in landmarks:
        if not landmark.get_observed():
            landmark.decrease_life()
        if landmark.get_life() <= 0:
            removed.append(landmark)
            landmarks.remove(landmark)


def landmarks_keep(lmks, landmarks, landmarkDB, landmarkNumber, init):
    tempLmks = []
    ID = landmarkNumber
    copyList = landmarks.copy()
    removed = []
    i = 0
    j = 0
    equal = False
    firstRun = init
    for lmk in lmks:
        temp = Landmark(lmk, ID)
        tempLmks.append(temp)
        ID += 1
    if len(landmarks) > 0:
        for lmk in tempLmks:
            j = 0
            while j < len(landmarks) and not equal:
                equal = lmk.same(landmarks[j])  # Here the observed flag is set to False
                #if not equal: # Decrese landmark life and remove it from the database it its life has droped to zero
                    #landmarks[j].decrease_life()
                j += 1
            if equal:  # If the lmk is the same as one already in the list, increase the latter observed count
                landmarks[j - 1].reset_life()
                if firstRun:
                    add2DB = landmarks[j-1].observed()
                    if add2DB and landmarks[j-1] not in landmarkDB:
                        landmarkDB.append(landmarks[j-1])
        removed = landmarks_track(landmarks)
        if firstRun:  # removes the removed landmarks also from the DB 
            for lmk in removed:
                if lmk in landmarkDB:
                    landmarkDB.remove()

    else:
        landmarks.extend(temp) # places the landmarks in the list one by one, instead as a list of lmks
