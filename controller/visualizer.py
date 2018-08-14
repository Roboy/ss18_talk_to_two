import threading
from queue import Queue
from queue import Empty
import time
import numpy as np 
from mpl_toolkits.mplot3d import Axes3D
import matplotlib
import matplotlib.cm as cm
import matplotlib.pyplot as plt



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
            latest_id = self.inq.get(block=True) 
            
            #sometime multiple rrive at once, make sure to clear the que and only use the latest one
            while 1:
                try:
                    latest_id = self.inq.get(block=False)  
                except Empty:
                    break
                
            data = []
            for i in range(len(latest_id['src'])):
                #{ "id": 53, "tag": "dynamic", "x": -0.828, "y": -0.196, "z": 0.525, "activity": 0.926 }   
                if latest_id['src'][i]['id'] > 0:
                    data.append([latest_id['src'][i]['id'], latest_id['src'][i]['x'], latest_id['src'][i]['y'], latest_id['src'][i]['z'], latest_id['src'][i]['activity'] ])
                if len(data) == 0:
                    data.append([0,0,0,0,0])
    
            sources = np.array(data)
                
            ax.clear()
            #add big center point in front
            plotsources = np.vstack((np.array([0, 0, 0, 0, 2]), sources)) #center point
            ax.scatter(plotsources[:,1], plotsources[:,2], plotsources[:,3], s=plotsources[:,4]*150+50, c=plotsources[:,4], cmap=cm.cool)
            for i in range(1, plotsources.shape[0]): #display the assigned id
                ax.text(plotsources[i,1],plotsources[i,2],plotsources[i,3],  '%s, %s' % (str(int(plotsources[i,0])), str(plotsources[i,4])), size=20) 
            ax.set_xlim3d(-1.2,1.2) #dont know why, but otherwise it keeps changin them...
            ax.set_ylim3d(-1.2,1.2)
            ax.set_zlim3d(-1.2,1.2) 
            #plt.pause(0.00001)
            fig.canvas.draw()
            print("drew")
            
            
            
            #print("elapsed time:", time.time() - last_time)
            #last_time = time.time()
            
        plt.close()
        print("stopping visulaization")
        
        
    def stop(self):
        self.please_stop.set()
        
        
        