

#import threading
import time
import numpy as np 
from queue import Queue
from queue import Empty

from audio_receiver import Audio_Receiver
from id_receiver import Id_Receiver
from speaker import Speaker
from visualizer import Visualizer
    

class Controller:
    
    def __init__(self):
        self.id_to_main_queue = Queue(maxsize=50)
        self.id_to_vis_queue = Queue(maxsize=50)
        self.audio_to_main_queue = Queue(maxsize=1000)
        self.id_recv = Id_Receiver(self.id_to_main_queue, self.id_to_vis_queue)
        self.audio_recv = Audio_Receiver(self.audio_to_main_queue)
        self.visualizer = Visualizer(self.id_to_vis_queue)
        self.speakers = []
        self.num_speakers = 0
        
    def run(self):
        self.id_recv.start()
        self.audio_recv.start()
        self.visualizer.start()
        
        recording_id_odas = [0, 0, 0, 0]
        recording_id_us = [0, 0, 0, 0]
        
        
        while self.id_recv.is_alive() and self.audio_recv.is_alive():
            
            #wait for new audio data
            latest_audio = self.audio_to_main_queue.get(block=True)
            
            #get the latest id update (empties queue and save the last one)
            while 1:
                try:
                    latest_id = self.id_to_main_queue.get(block=False)  
                except Empty:
                    break
            ##TODO tag and feed to new channels and update our ids
            for i in range(len(latest_id['src'])):  #len=4
            #{ "id": 53, "tag": "dynamic", "x": -0.828, "y": -0.196, "z": 0.525, "activity": 0.926 }   
                recording_id_odas[i] = latest_id['src'][i]['id']

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
                    

            
            
            
            
        print("done.")
        self.id_recv.stop()
        self.audio_recv.stop()
        self.visualizer.stop()
        
    
    
        
