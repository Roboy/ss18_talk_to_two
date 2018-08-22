import threading
from Queue import Queue
from Queue import Empty
import socket 
import numpy as np 

class Audio_Receiver(threading.Thread):
    
    def __init__(self, outq):
        threading.Thread.__init__(self)
        self.outq = outq
        self.please_stop = threading.Event()

    def run(self):
        
        print('Audio receiver waiting for connection...')
        
        HOST = ''
        TCP_PORT = 9002
        BUFFER_SIZE = 1024*64  
    
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, TCP_PORT))
        s.listen(1)
        
        conn, addr = s.accept()
        print('Audio Connection address audio:', addr)
        
        #we assume we always get a multiple of 512 samples, if not the remainder will be stored in  this buffer
        channel_buffer_feeder = [np.array([0,0], dtype=np.int16), np.array([0,0], dtype=np.int16), np.array([0,0], dtype=np.int16), np.array([0,0], dtype=np.int16)]
        
        while not self.please_stop.is_set():
            
            data = conn.recv(BUFFER_SIZE)
            #print (data)
            if not data: break

            dataarray = np.frombuffer(data, dtype=np.int16)
            
            #first put all data into my buffer
            for i in range(4):
                channel_buffer_feeder[i] = np.append(channel_buffer_feeder[i], dataarray[i::4])
            #if my buffer has more than 512 samples feed them into the queue
            while len(channel_buffer_feeder[0]) >= 512:
                #check if there is space in queue, if not clear some
                if self.outq.qsize() > self.outq.maxsize-10: 
                        print("audio queue has grown to large, discarding some.")
                        for i in range(10): #q is almost full, discard some data
                            try:
                                self.outq.get(block=False)  
                            except Empty:
                                pass
                #we have enough samples, so put list into queue
                self.outq.put([channel_buffer_feeder[0][:512], channel_buffer_feeder[1][:512], channel_buffer_feeder[2][:512], channel_buffer_feeder[3][:512]])
                #delete them from our buffer
                for i in range(4):
                    channel_buffer_feeder[i] = channel_buffer_feeder[i][512:]
                            
    
        conn.close()
        
        if not self.please_stop.is_set():
            print("Audio connection closed externally")
        else:
            print("Stopping Audio thread as requested by main")

        
    def stop(self):
        self.please_stop.set()
        
        