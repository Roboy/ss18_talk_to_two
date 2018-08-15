

#import threading
import time
import numpy as np 
from Queue import Queue
from Queue import Empty
from Queue import Full

from merger import Merger
from visualizer import Visualizer
from speaker import Speaker
from recording import Recording

from speaker_recognition_new.speaker_recognition import Speaker_recognition


    

class Worker:
    
    def __init__(self, visualization=True):
        self.merger_to_main_queue = Queue(maxsize=1000) #very roughly 30sec
        self.merger = Merger(self.merger_to_main_queue)
        
        self.visualization = visualization
        if self.visualization:
            self.main_to_vis_queue = Queue(maxsize=50)
            self.visualizer = Visualizer(self.main_to_vis_queue)
              
        self.speakers = {}
        self.num_speakers = 0
        self.sr = Speaker_recognition()
        
    def run(self):
        self.merger.start()
        
        if self.visualization:
            self.visualizer.start()
        
        recording_id_odas = [0, 0, 0, 0]
        last_recording_id_odas = [0, 0, 0, 0]
        
        recordings = {}
        sr_requests = {} #request to speaker recognotiotion waiting to be anawered, key is the id, value is the queue in which the result will be stored
        
        while self.merger.is_alive():
            
            #wait for/get next data
            next_data = self.merger_to_main_queue.get(block=True)
            cid = next_data['id_info']
            caudio = next_data['audio_data']
            
            
            #this part separates the 4 streams and manages the ones where currently audio is being recorded
            #cid[i] = [id, x, y, z, activity]
            for i in range(len(cid)):  #len=4
                
                recording_id_odas[i] = cid[i][0]
                
                if recording_id_odas[i] > 0:
                    if recording_id_odas[i] == last_recording_id_odas[i]:
                        #same person continues speaking
                        recordings[recording_id_odas[i]].audio = np.append(recordings[recording_id_odas[i]].audio, caudio[i])
                        recordings[recording_id_odas[i]].currentpos = [cid[i][1], cid[i][2], cid[i][3]]
                
                    else:
                        #a person startet speaking
                        recordings[recording_id_odas[i]] = Recording(recording_id_odas[i], [cid[i][1], cid[i][2], cid[i][3]])
                        recordings[recording_id_odas[i]].audio = np.append(recordings[recording_id_odas[i]].audio, caudio[i])
                        
                        #if a different person was speaking before, he is now done
                        if last_recording_id_odas[i] > 0:
                            recordings[last_recording_id_odas[i]].stopped = True
                elif recording_id_odas[i] == 0 and last_recording_id_odas[i] > 0:
                    #if a different person was speaking before, he is now done
                    recordings[last_recording_id_odas[i]].stopped = True
                    
                last_recording_id_odas[i] = recording_id_odas[i]
                    
                    
            #check if we got any ansers from sr (speaker recognition) in the meantime
            todelete_req = []
            for rec_id, req in sr_requests.iteritems():
                try:
                    #sr_id: -99 means new speaker
                    #certainty between 0-10
                    certainty = 0
                    preliminary_id, sr_id, certainty = req.get(block=False) 
                    #TODO:merge these two infos together
                    if certainty < 3:
                        recordings[rec_id].final_speaker_id = recordings[rec_id].preliminary_speaker_id
                    print("response for req %d, results is" % (rec_id))    
                    recordings[rec_id].is_back_from_sr = True
                    todelete_req.append(rec_id)
                    
                except Empty:
                    if time.time() - recordings[rec_id].time_sent_to_sr > 10: #no response from sr for 10 sec -> timeout
                        print("no response for request %d in 10 sec -> timeout" % (rec_id))
                        recordings[rec_id].final_speaker_id = recordings[rec_id].preliminary_speaker_id
                        recordings[rec_id].is_back_from_sr = True
                        todelete_req.append(rec_id)
                    
            for req in todelete_req:
                del sr_requests[req]
                    
                    
                    
                    
            #here we go through our recordings and try to assign speakers
            todelete = []
            if self.visualization:
                rec_info_to_vis = [] 
            for rec_id, rec in recordings.iteritems():
                if rec.new:
                    print("new recording ", rec_id)
                    #get angles to all known speakers
                    rec.get_angles_to_all_speakers(self.speakers, rec.startpos)
                    
                    #if it is wihthin a certain range to a known speaker, assign it to him
                    if len(self.speakers)>0 and rec.angles_to_speakers[0][1] < 25: #degree
                        print("preliminary assigning recording %d to speaker %d" % (rec_id, rec.angles_to_speakers[0][0]))
                        rec.preliminary_speaker_id = rec.angles_to_speakers[0][0]
                        
                    else:
                        #create a new speaker
                        self.num_speakers += 1
                        new_id = self.num_speakers
                        self.speakers[new_id] = Speaker(new_id, rec.startpos)
                        rec.preliminary_speaker_id = new_id
                        rec.created_new_speaker = True
                        print("creating new speaker %d for recording %d" % (new_id, rec_id))
                        
                    rec.new = False
                    
                    
                elif not rec.was_sent_sr and rec.audio.shape[0] > 16000 * 3: #its longer than 3 sec, time to send it to speaker recognition
                    sr_requests[rec_id] = Queue(maxsize=1)
                    #dummy_sr_call(rec.audio, rec.preliminary_speaker_id, sr_requests[rec_id])
                    self.sr.test(rec.audio, rec.preliminary_speaker_id, sr_requests[rec_id])
                    rec.was_sent_sr = True
                    rec.time_sent_to_sr = time.time()
                    
                elif rec.stopped:       
                #speaker finished, hanlde this
                    if not rec.alldone:
                        if rec.audio.shape[0] < 16000 * 0.4: #everything shorter than this we simply discard
                            print("recording %d was too short, discarding" % (rec_id))
                            if rec.created_new_speaker:
                                del self.speakers[rec.preliminary_speaker_id]
                                print("thus also deleting seaker", rec.preliminary_speaker_id )
                            rec.alldone = True
                    if not rec.alldone:    
                        if (rec.was_sent_sr and rec.is_back_from_sr) or (not rec.was_sent_sr):
                            if not rec.was_sent_sr:
                                #it seems like this has been to short to be sent to
                                rec.final_speaker_id = rec.preliminary_speaker_id
                            self.speakers[rec.final_speaker_id].pos = rec.currentpos
                            
                            #TODO:
                            #send to speech to text
                            print("succesfully handeld recording ", rec_id)
                            rec.alldone = True
                            
                        else:
                            pass #wait for the response of sr
            
                
                if rec.alldone:
                    todelete.append(rec_id)
                    
                if self.visualization:
                    rec_info_to_vis.append([rec_id, rec.currentpos[0], rec.currentpos[1], rec.currentpos[2], 200])#200 is the size of the blob
            
            for rec_id in todelete:
                del recordings[rec_id]
                
            if self.visualization:
                try:        
                    self.main_to_vis_queue.put({'speakers': self.speakers, 'recordings': rec_info_to_vis}, block=False)
                except Full:
                    #print("couldn't put data into visualization queue, its full")
                    pass
                
                
            
            
        print("Worker is done.")
        self.merger.stop()
        if self.visualization:
            self.visualizer.stop()
            
            
            

    
        
