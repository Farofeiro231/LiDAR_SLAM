import numpy as np

LIFE = 40

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
    
    def observed():
        self.timesObserved += 1

    def dying():
        if self.life > 0:
            self.life -= 1

