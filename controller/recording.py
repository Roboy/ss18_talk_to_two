import numpy as np 
from operator import itemgetter

class Recording:
    def __init__(self, odas_id, startpos):
        self.odas_id = odas_id
        self.startpos = startpos
        self.currentpos = startpos
        self.audio = np.empty(0, dtype=np.int16)
        self.stopped = False
        self.alldone = False
        self.was_sent_sr = False
        self.is_back_from_sr = False
        self.time_sent_to_sr = 0
        self.new = True
        self.preliminary_speaker_id = 0
        self.final_speaker_id = 0
        self.created_new_speaker = False
        self.angles_to_speakers = []
        
        
    #redurns a list of soerted touples (speaker_id, angle)
    def get_angles_to_all_speakers(self, speakers, pos):
        angles = []
        for sp_id, sp in speakers.iteritems():
            angles.append( (sp_id, sp.get_angle_to(pos)) )
        self.angles_to_speakers =  sorted(angles, key=itemgetter(1))
        return self.angles_to_speakers
        
        