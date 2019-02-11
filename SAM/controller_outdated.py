

#import threading
import time
import numpy as np 
from Queue import Queue
from Queue import Empty
from Queue import Full

from audio_receiver import Audio_Receiver
from id_receiver import Id_Receiver
from speaker import Speaker
from visualizer import Visualizer
    

class Controller:
    
    def __init__(self, visualization=True):
        self.id_to_main_queue = Queue(maxsize=50)  
        self.audio_to_main_queue = Queue(maxsize=1000)
        self.id_recv = Id_Receiver(self.id_to_main_queue)
        self.audio_recv = Audio_Receiver(self.audio_to_main_queue)
        
        self.visualization = visualization
        if self.visualization:
            self.main_to_vis_queue = Queue(maxsize=50)
            self.visualizer = Visualizer(self.main_to_vis_queue)
              
        self.speakers = []
        self.num_speakers = 0
        
    def run(self):
        self.id_recv.start()
        self.audio_recv.start()
        
        if self.visualization:
            self.visualizer.start()
        
        recording_id_odas = [0, 0, 0, 0]
        recording_id_us = [0, 0, 0, 0]
        last_recording_id_us = [0, 0, 0, 0]
        
        
        while self.id_recv.is_alive() and self.audio_recv.is_alive():
            
            #wait for new audio data
            latest_audio = self.audio_to_main_queue.get(block=True)
            
            audio_recording_buffer = [np.empty(0, dtype=np.int16), np.empty(0, dtype=np.int16), np.empty(0, dtype=np.int16), np.empty(0, dtype=np.int16)]
            
            #get the latest id update (empties queue and save the last one)
            while 1:
                try:
                    latest_id = self.id_to_main_queue.get(block=False)  
                except Empty:
                    break
            
            if self.visualization:
                current_speakers = []
            
            
            #this part filters the odas source tracking and assigs our filtered speaker id to each odas source
            for i in range(len(latest_id['src'])):  #len=4
            #{ "id": 53, "tag": "dynamic", "x": -0.828, "y": -0.196, "z": 0.525, "activity": 0.926 }   
                recording_id_odas[i] = latest_id['src'][i]['id']
                recording_id_us[i] = 0 #clear our ids

                if recording_id_odas[i] > 0:
                    thispos = [latest_id['src'][i]['x'], latest_id['src'][i]['y'], latest_id['src'][i]['z']]
                    #check if we know this speaker id, and if yes update our speaker
                    found_matching_speaker = False
                    for speaker in self.speakers:
                        if speaker.current_odas_id == recording_id_odas[i]:
                            recording_id_us[i] = speaker.id
                            speaker.pos = thispos
                            found_matching_speaker = True
                            break
                        
                 #TODO: if to speakers drifted close together and became inactive, how to decide, which one it is now
                    if not found_matching_speaker:
                        #check if it mathces a certain angle threshold to one of our speakers
                        closest_dist = 10
                        for speaker in self.speakers:
                            dist = speaker.get_dist_to(thispos)
                            if dist < closest_dist:
                                closest_dist = dist
                                closest_id = speaker.id
                                
                            if dist < 0.54:  # 0.54 is roughly 10 degrees
                                speaker.current_odas_id = recording_id_odas[i]
                                recording_id_us[i] = speaker.id
                                speaker.pos = thispos
                                found_matching_speaker = True
                                print("is matching %d" % (speaker.id))
                                break
                            
                    if not found_matching_speaker:
                        #this speaker does not exist, create a new one
                        self.num_speakers += 1
                        print("Found new speaker: %d, pos: %f, %f, %f" % (self.num_speakers, thispos[0], thispos[1], thispos[2]))
                        if closest_dist > 1.3: #1.3 is roughtly 30 dgree
                            self.speakers.append(Speaker(self.num_speakers, thispos, recording_id_odas[i]))
                            recording_id_us[i] = self.num_speakers
                        else:
                            self.speakers.append(Speaker(self.num_speakers, thispos, recording_id_odas[i], closest_dist, closest_id))
                            recording_id_us[i] = self.num_speakers
                    
                    if self.visualization:
                        #at this point we have assigned our speaker id, so save this information for the visualization thread
                        current_speakers.append([recording_id_us[i], latest_id['src'][i]['id'], latest_id['src'][i]['x'], latest_id['src'][i]['y'], latest_id['src'][i]['z'], latest_id['src'][i]['activity'] ])
                        
                        
            #put data in the que for the visualizer
            if self.visualization:
                try:
                    
                    self.main_to_vis_queue.put({'current_speakers': current_speakers, 'known_speakers': self.speakers, 'num_known_speakers': self.num_speakers}, block=False)
                except Full:
                    #print("couldn't put data into visualization queue, its full")
                    pass
                
                
                
                
            #record audio of currently active speakers
            for i in range(len(recording_id_us)):
                if recording_id_us[i] > 0:
                    audio_recording_buffer[i] = np.append(audio_recording_buffer[i], latest_audio[i])
                
                #if a speaker stopped speaking send the chunk off
                if recording_id_us[i] == 0 and last_recording_id_us[i] > 0:
                    
                    #TODO send this somewhere
                    #clear this recording buffer
                    audio_recording_buffer[i] = np.empty(0, dtype=np.int16)
                    
                #check if one channel has been active for too long, then cut it and send it
                if audio_recording_buffer[i].shape[0] > 16000 * 60: #cut after 60 seconds
                    
                    #TODO send this somewhere
                    #clear this recording buffer
                    audio_recording_buffer[i] = np.empty(0, dtype=np.int16)
                    
                last_recording_id_us[i] = recording_id_us[i]
                    
                    
                    
                
                    

            
            
            
            
        print("done.")
        self.id_recv.stop()
        self.audio_recv.stop()
        if self.visualization:
            self.visualizer.stop()
        
    
    
        
