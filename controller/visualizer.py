import threading
from Queue import Queue
from Queue import Empty
import time
import numpy as np 

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

#matplotlib.use("gtk")



class Visualizer(threading.Thread):
    
    def __init__(self, inq):
        threading.Thread.__init__(self)
        self.inq = inq
        self.please_stop = threading.Event()

    def run(self):
        
        
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        plt.ion()
        ax.autoscale(enable=False)
        ax.set_xlim3d(-1.2,1.2)
        ax.set_ylim3d(-1.2,1.2)
        ax.set_zlim3d(-1.2,1.2)
        
        fig.show()
        fig.canvas.draw()
        
        #last_time = time.time()
        
        
        while not self.please_stop.is_set():
            #wait for data to arrive
            latest_data = self.inq.get(block=True) 
            
            #sometime multiple rrive at once, make sure to clear the que and only use the latest one
            while 1:
                try:
                    latest_data = self.inq.get(block=False)  
                except Empty:
                    break
            
            
                
            speakers_for_vis = []
            speakers_for_vis.append([0, 0, 0, 0, 300])#center point
            for sp_id, sp in latest_data['speakers'].iteritems():
                speakers_for_vis.append([sp_id, sp.pos[0], sp.pos[1], sp.pos[2], 100])
                
            rec_for_vis = latest_data['recordings']
            
                
            ax.clear()        
            #TODO: fic colors
            if(len(speakers_for_vis) > 0):
                speakers_for_vis = np.array(speakers_for_vis)
                ax.scatter(speakers_for_vis[:,1], speakers_for_vis[:,2], speakers_for_vis[:,3], s=speakers_for_vis[:,4])
                for sp in speakers_for_vis: #display the assigned id
                    if sp[0] > 0:
                        ax.text(sp[1],sp[2],sp[3],  '%s' % (str(int(sp[0]))), size=15) 
            if(len(rec_for_vis) > 0):
                rec_for_vis = np.array(rec_for_vis)
                ax.scatter(rec_for_vis[:,1], rec_for_vis[:,2], rec_for_vis[:,3], s=rec_for_vis[:,4])
                for rec in rec_for_vis: #display the assigned id
                    ax.text(rec[1],rec[2],rec[3],  '%s' % (str(int(rec[0]))), size=15, color='red') 
            ax.set_xlim3d(-1.2,1.2) #dont know why, but otherwise it keeps changin them...
            ax.set_ylim3d(-1.2,1.2)
            ax.set_zlim3d(-1.2,1.2) 
            plt.pause(0.001)
            fig.canvas.draw()
            
            
            
            #print("elapsed time:", time.time() - last_time)
            #last_time = time.time()
            
        plt.close()
        print("stopping visulaization")
        
        
    def stop(self):
        self.please_stop.set()
        
        
        