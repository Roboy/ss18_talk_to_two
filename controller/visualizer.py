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
            
            
            """
            data = []
            for i in range(len(latest_id['src'])):
                #{ "id": 53, "tag": "dynamic", "x": -0.828, "y": -0.196, "z": 0.525, "activity": 0.926 }   
                if latest_id['src'][i]['id'] > 0:
                    data.append([latest_id['src'][i]['id'], latest_id['src'][i]['x'], latest_id['src'][i]['y'], latest_id['src'][i]['z'], latest_id['src'][i]['activity'] ])
                if len(data) == 0:
                    data.append([0,0,0,0,0])
            """
    
            sources = np.array(latest_data['current_speakers'])
            if sources.size == 0:
                sources = np.array([0, 0, 0, 0, 0, 0])
                
            ax.clear()
            #add big center point in front
            #array is   ourid, odasid, x,y,z,activity
            plotsources = np.vstack((np.array([0, 0, 0, 0, 0, 2]), sources)) #center point
            
            #array for plotting all known speakers:
            speakerplot = []
            for sp in latest_data['known_speakers']:
                speakerplot.append([sp.id, 0, sp.pos[0], sp.pos[1], sp.pos[2], 0])
            np_speakerplot = np.array(speakerplot)
            
            #TODO: fic colors
            if(len(speakerplot) > 0):
                ax.scatter(np_speakerplot[:,2], np_speakerplot[:,3], np_speakerplot[:,4], s=100, c=np_speakerplot[:,0], cmap=cm.Pastel1)
                
            ax.scatter(plotsources[:,2], plotsources[:,3], plotsources[:,4], s=plotsources[:,5]*150+50, c=plotsources[:,0], cmap=cm.Set1)
            for sp in latest_data['known_speakers']: #display the assigned id
                ax.text(sp.pos[0],sp.pos[1],sp.pos[2],  '%s' % (str(int(sp.id))), size=15) 
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
        
        
        