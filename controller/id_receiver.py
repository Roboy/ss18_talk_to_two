import threading
from Queue import Queue
from Queue import Empty
import socket
import json

class Id_Receiver(threading.Thread):
    
    def __init__(self, outq):
        threading.Thread.__init__(self)
        self.outq = outq
        self.please_stop = threading.Event()

    def run(self):
        
        print('Id receiver waiting for connection...')
                 
        HOST = ''
        TCP_PORT = 9003
        BUFFER_SIZE = 1024*16 
    
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, TCP_PORT))
        s.listen(1)
    
        #decoder = json.JSONDecoder()
        buffer = ''
        #last_time = time.time()
    
        #while 1: 
        conn, addr = s.accept()
        print('Id Connection address pos:', addr)
        
        while not self.please_stop.is_set():
            
            data = conn.recv(BUFFER_SIZE)
            if not data: break
            #clear_output()
            #print("received data")
            buffer += data.decode("utf-8")
            #one sst info block are 411 bytes, but sometimes more than one/fragments arrive at once
            #print("buffer len  pre:",len(buffer))
    
            success = True
            while success: #loop, because sometime more than one packege arrives at once
                [buffer, success, res] = self.dynamic_json_extractor(buffer)
                if success:
                    #print("got smth")
                    latest_sound_source_data = json.loads(res)
                    #print("elapsed time:", time.time() - last_time)
                    #last_time = time.time()
                    if self.outq.qsize() > self.outq.maxsize-20: 
                        print("id queue has grown to large, discarding some, this should rarely happen!!!!!!")
                        for i in range(20): #q is almost full, discard some data
                            try:
                                self.outq.get(block=False)  
                            except Empty:
                                pass
                    self.outq.put(latest_sound_source_data) #this is blocking and thread safe
                    
                    
            #print("buffer len post:",len(buffer))
            
        conn.close()
        if not self.please_stop.is_set():
            print("Id connection closed externally")
        else:
            print("Stopping Id thread as requested by main")
            
        
        
    def stop(self):
        self.please_stop.set()
        
        
    #the data we receive over the netowrk does not neatly aling with the json objects, so je need to search the buffer for valid objects
    def dynamic_json_extractor(self, buffer):
        
        if len(buffer) > 10000:
            #if the buffer has gotten too large (thats over 20 messages) somethin obviously has gone wrong, (mybe something misformatted?) and we should discard this
            print("Buffer has grown too large, something must have gone wrong, clearing buffer. Buffer size was", len(buffer))
            buffer = ''
        
        timeStamp_ind = buffer.find('timeStamp')
        if timeStamp_ind > -1:
            start = buffer.rfind('{', 0, timeStamp_ind) #find last { before timstamp (json obj starts here)
            if start > -1:
                buffer = buffer[start:]  #discard everything before (cannot be full object anymore)
                #now got through the whole buffer, and see count brackets, until you find the matching closing one
                count = 0
                end_index = 0;
                success = False
                for c in buffer:
                    if c == '{':
                        count += 1
                    if c == '}':
                        count -= 1
                    if count == 0:
                        success = True
                        break;
                    end_index += 1
                if success:
                    final_json = buffer[:end_index+1]
                    buffer = buffer[end_index+1:]
                    #print("extracted:", final_json)
                    #print("buffer   :", buffer)
                    return [buffer, True, final_json]
        return[buffer, False, None]