import numpy as np

SEEN = 10 # Good value to avoid miss insertions
LIFE = 40 # Now for the life to be decreased the lmk needs to go unseen through a whole sweep
TOLERANCE_A = 0.1
TOLERANCE_B = 50
TOLERANCE = 100 # Bom valor é 100
ORIG_THRESHOLD = 200
DIR_THRESHOLD = 0.1


class Landmark():
    spec = "line"

    def __init__(self, lm_orig, lm_dir, ID):
        self.orig = lm_orig
        self.dir = lm_dir
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

    def get_orig(self):
        return self.orig
   
    def get_dir(self):
        return self.dir

    def get_end(self):
        return self.end

    def get_life(self):
        return self.life

    def get_observed(self):
        return self.observed
    
    def seen(self):
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
    
    def distance_origin_origin(self, landmark):
        distance = np.linalg.norm(self.orig - landmark.get_orig())
        return distance
#    
    def distance_dirs(self, landmark):
        distance = np.linalg.norm(np.absolute(self.dir) - np.absolute(landmark.get_dir()))
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
        if self.distance_origin_origin(landmark) < TOLERANCE and self.distance_dir_dir(landmark) < TOLERANCE:
            #if distanceOriginEnd <= TOLERANCE or distanceEndOrigin <= TOLERANCE:
                return True
        else:
                return False

    def same(self, lmk):
        distOrig = self.distance_origin_origin(lmk)
        distDir = self.distance_dirs(lmk)
        if distOrig < ORIG_THRESHOLD and distDir < DIR_THRESHOLD:
            #print("DistOrig: {}".format(distOrig))
            #print("DistDir: {}".format(distDir))
            return True
        else:
            return False
    
    def same_update(self, lmk, tolerance):
        distOrig = self.distance_origin_origin(lmk)
        distDir = self.distance_dirs(lmk)
        if distOrig < tolerance and distDir < DIR_THRESHOLD:
            return True
        else:
            return False




    def same_decomposed(self, orig, direction):
        distOrig = np.linalg.norm(self.get_orig() - orig)
        distDir  = np.linalg.norm(self.get_dir() - direction)
        if distOrig <= ORIG_THRESHOLD and distDir <= DIR_THRESHOLD:
            return True
        else:
            return False


def renew_lmks(landmarks):
    for lmk in landmarks:
        lmk.observed = False


def landmarks_track(landmarks):
    removed = [] 
    for landmark in landmarks:
        if not landmark.get_observed():
            landmark.decrease_life()
        if landmark.get_life() <= 0:
            removed.append(landmark)
            landmarks.remove(landmark)
    return removed


def landmarks_keep(lmks, landmarks, landmarkDB, landmarkNumber, firstRun):
    tempLmks = []
    ID = float(landmarkNumber)
    copyList = landmarks.copy()
    removed = []
    i = 0
    j = 0
    equal = False
    for lmk in lmks:
        temp = Landmark(lmk[0], lmk[1], ID)
        tempLmks.append(temp)
        ID += 1
    if len(landmarks) > 0:
        renew_lmks(landmarks)
        for lmk in tempLmks:
            j = 0
            while j < len(landmarks) and not equal:
                equal = lmk.same(landmarks[j])  # Here the observed flag is set to False
                j += 1
            if equal:  # If the lmk is the same as one already in the list, increase the latter observed count
                landmarks[j - 1].reset_life()
                if firstRun:
                    add2DB = landmarks[j-1].seen()
                    if add2DB and landmarks[j-1] not in landmarkDB:
                        print("--------------Added landmark-----------")
                        print(landmarks[j-1])    
                        landmarkDB.append(landmarks[j-1])
            else: # if it is a new landmark, add it to the list
                landmarks.append(lmk)
        removed = landmarks_track(landmarks) #remove dead landmarks
        if firstRun:  # removes the removed landmarks also from the DB 
            for lmk in removed:
                if lmk in landmarkDB:
                    print("--------------Removed landmark-----------")
                    print(lmk)
                    landmarkDB.remove(lmk)
    else:
        landmarks.extend(tempLmks) # places the landmarks in the list one by one, instead as a list of lmks


def lmks_keep_match(lmks, landmarks, landmarkNumber):
    ID = float(landmarkNumber)
    tempLmks = []

    for lmk in lmks:
        temp = Landmark(lmk[0], lmk[1], ID)
        tempLmks.append(temp)
        ID += 1

    del landmarks[:]
    landmarks.extend(tempLmks)

