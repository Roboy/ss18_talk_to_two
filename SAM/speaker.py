
import time
import math

class Speaker:
    
    #this is designed to be called the first time a new speaker actually speaks
    #pos is a list of [x, y, z]
    def __init__(self, myid, pos):
        self.id = myid
        self.pos = pos
        self.last_active = time.time()
        self.isconfirmed = False
    
    def get_angle_to(self, otherpos):
        #normally you should devide by the norm of the vectors, but its always very close to one
        norm = math.sqrt(self.pos[0]**2 + self.pos[1]**2 + self.pos[2]**2) * math.sqrt(otherpos[0]**2 + otherpos[1]**2 + otherpos[2]**2)
        return abs(180*math.acos(((self.pos[0] * otherpos[0]) + (self.pos[1] * otherpos[1]) + (self.pos[2] * otherpos[2])) / norm)/math.pi)
        
