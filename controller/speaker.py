
import time
import math

class Speaker:
    
    #this is designed to be called the first time a new speaker actually speaks
    #pos is a list of [x, y, z]
    def __init__(self, myid, pos, current_odas_id, unsure_if_new=0, closest_id=None):
        self.id = myid
        self.pos = pos
        self.last_active = time.time()
        self.current_odas_id = current_odas_id
        self.unsure_if_new = unsure_if_new #this is the distacne to the closest old speaker, the smaller it is, the less sure we are
        self.closest_id = closest_id
    
    def get_dist_to(self, otherpos):
        return math.sqrt((self.pos[0]-otherpos[0])**2 + (self.pos[1]-otherpos[1])**2 + (self.pos[2]-otherpos[2])**2 )
        
