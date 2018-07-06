
# coding: utf-8

# In[1]:

import numpy
import sklearn.cluster
import time
import scipy
import os
import pyAudioAnalysis
import pyAudioAnalysis.audioFeatureExtraction as aF
import pyAudioAnalysis.audioTrainTest as aT
import pyAudioAnalysis.audioBasicIO
import matplotlib.pyplot as plt
from scipy.spatial import distance
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import sklearn.discriminant_analysis
import csv
import os.path
import sklearn
import sklearn.cluster
import hmmlearn.hmm
import cPickle
import glob
import pyaudio
import wave 
import Tkinter as tk
import time
import ttk


# In[3]:

def trainHMM_computeStatistics(features, labels):
    '''
    This function computes the statistics used to train an HMM joint segmentation-classification model
    using a sequence of sequential features and respective labels

    ARGUMENTS:
     - features:    a numpy matrix of feature vectors (numOfDimensions x numOfWindows)
     - labels:    a numpy array of class indices (numOfWindows x 1)
    RETURNS:
     - startprob:    matrix of prior class probabilities (numOfClasses x 1)
     - transmat:    transition matrix (numOfClasses x numOfClasses)
     - means:    means matrix (numOfDimensions x 1)
     - cov:        deviation matrix (numOfDimensions x 1)
    '''
    uLabels = numpy.unique(labels)
    nComps = len(uLabels)

    nFeatures = features.shape[0]

    if features.shape[1] < labels.shape[0]:
        print "trainHMM warning: number of short-term feature vectors must be greater or equal to the labels length!"
        labels = labels[0:features.shape[1]]

    # compute prior probabilities:
    startprob = numpy.zeros((nComps,))
    for i, u in enumerate(uLabels):
        startprob[i] = numpy.count_nonzero(labels == u)
    startprob = startprob / startprob.sum()                # normalize prior probabilities

    # compute transition matrix:
    transmat = numpy.zeros((nComps, nComps))
    for i in range(labels.shape[0]-1):
        transmat[int(labels[i]), int(labels[i + 1])] += 1
    for i in range(nComps):                     # normalize rows of transition matrix:
        transmat[i, :] /= transmat[i, :].sum()

    means = numpy.zeros((nComps, nFeatures))
    for i in range(nComps):
        means[i, :] = numpy.matrix(features[:, numpy.nonzero(labels == uLabels[i])[0]].mean(axis=1))

    cov = numpy.zeros((nComps, nFeatures))
    for i in range(nComps):
        #cov[i,:,:] = numpy.cov(features[:,numpy.nonzero(labels==uLabels[i])[0]])  # use this lines if HMM using full gaussian distributions are to be used!
        cov[i, :] = numpy.std(features[:, numpy.nonzero(labels == uLabels[i])[0]], axis=1)

    return startprob, transmat, means, cov


# In[4]:

#def speakerDiarization(fileName, numOfSpeakers, mtSize=2.0, mtStep=0.2, stWin=0.05, LDAdim=35, PLOT=False):
def speakerDiarization(fileName, numOfSpeakers, mtSize=2.0, mtStep=0.2, stWin=0.05, LDAdim=0, PLOT=False):
    '''
    ARGUMENTS:
        - fileName:        the name of the WAV file to be analyzed
        - numOfSpeakers    the number of speakers (clusters) in the recording (<=0 for unknown)
        - mtSize (opt)     mid-term window size
        - mtStep (opt)     mid-term window step
        - stWin  (opt)     short-term window size
        - LDAdim (opt)     LDA dimension (0 for no LDA)
        - PLOT     (opt)   0 for not plotting the results 1 for plottingy
    '''
    [Fs, x] = pyAudioAnalysis.audioBasicIO.readAudioFile(fileName)
    x = pyAudioAnalysis.audioBasicIO.stereo2mono(x)
    Duration = len(x) / Fs

    #[Classifier1, MEAN1, STD1, classNames1, mtWin1, mtStep1, stWin1, stStep1, computeBEAT1] = aT.loadKNNModel(os.path.join("data","knnSpeakerAll"))
    #[Classifier2, MEAN2, STD2, classNames2, mtWin2, mtStep2, stWin2, stStep2, computeBEAT2] = aT.loadKNNModel(os.path.join("data","knnSpeakerFemaleMale"))
    [Classifier1, MEAN1, STD1, classNames1, mtWin1, mtStep1, stWin1, stStep1, computeBEAT1] = aT.loadKNNModel("pyAudioAnalysis/data/knnSpeakerAll")
    [Classifier2, MEAN2, STD2, classNames2, mtWin2, mtStep2, stWin2, stStep2, computeBEAT2] = aT.loadKNNModel("pyAudioAnalysis/data/knnSpeakerFemaleMale")

    [MidTermFeatures, ShortTermFeatures] = aF.mtFeatureExtraction(x, Fs, mtSize * Fs, mtStep * Fs, round(Fs * stWin), round(Fs*stWin * 0.5))

    MidTermFeatures2 = numpy.zeros((MidTermFeatures.shape[0] + len(classNames1) + len(classNames2), MidTermFeatures.shape[1]))

    for i in range(MidTermFeatures.shape[1]):
        curF1 = (MidTermFeatures[:, i] - MEAN1) / STD1
        curF2 = (MidTermFeatures[:, i] - MEAN2) / STD2
        [Result, P1] = aT.classifierWrapper(Classifier1, "knn", curF1)
        [Result, P2] = aT.classifierWrapper(Classifier2, "knn", curF2)
        MidTermFeatures2[0:MidTermFeatures.shape[0], i] = MidTermFeatures[:, i]
        MidTermFeatures2[MidTermFeatures.shape[0]:MidTermFeatures.shape[0]+len(classNames1), i] = P1 + 0.0001
        MidTermFeatures2[MidTermFeatures.shape[0] + len(classNames1)::, i] = P2 + 0.0001

    MidTermFeatures = MidTermFeatures2    # TODO
    # SELECT FEATURES:
    #iFeaturesSelect = [8,9,10,11,12,13,14,15,16,17,18,19,20];                                                                                         # SET 0A
    #iFeaturesSelect = [8,9,10,11,12,13,14,15,16,17,18,19,20, 99,100];                                                                                 # SET 0B
    #iFeaturesSelect = [8,9,10,11,12,13,14,15,16,17,18,19,20, 68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,
    #   97,98, 99,100];     # SET 0C

    iFeaturesSelect = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53]                           # SET 1A
    #iFeaturesSelect = [8,9,10,11,12,13,14,15,16,17,18,19,20,41,42,43,44,45,46,47,48,49,50,51,52,53, 99,100];                                          # SET 1B
    #iFeaturesSelect = [8,9,10,11,12,13,14,15,16,17,18,19,20,41,42,43,44,45,46,47,48,49,50,51,52,53, 68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98, 99,100];     # SET 1C

    #iFeaturesSelect = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53];             # SET 2A
    #iFeaturesSelect = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53, 99,100];     # SET 2B
    #iFeaturesSelect = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53, 68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98, 99,100];     # SET 2C

    #iFeaturesSelect = range(100);                                                                                                    # SET 3
    #MidTermFeatures += numpy.random.rand(MidTermFeatures.shape[0], MidTermFeatures.shape[1]) * 0.000000010

    MidTermFeatures = MidTermFeatures[iFeaturesSelect, :]

    (MidTermFeaturesNorm, MEAN, STD) = aT.normalizeFeatures([MidTermFeatures.T])
    MidTermFeaturesNorm = MidTermFeaturesNorm[0].T
    numOfWindows = MidTermFeatures.shape[1]

    # remove outliers:
    DistancesAll = numpy.sum(distance.squareform(distance.pdist(MidTermFeaturesNorm.T)), axis=0)
    MDistancesAll = numpy.mean(DistancesAll)
    iNonOutLiers = numpy.nonzero(DistancesAll < 1.2 * MDistancesAll)[0]

    # TODO: Combine energy threshold for outlier removal:
    #EnergyMin = numpy.min(MidTermFeatures[1,:])
    #EnergyMean = numpy.mean(MidTermFeatures[1,:])
    #Thres = (1.5*EnergyMin + 0.5*EnergyMean) / 2.0
    #iNonOutLiers = numpy.nonzero(MidTermFeatures[1,:] > Thres)[0]
    #print iNonOutLiers

    perOutLier = (100.0 * (numOfWindows - iNonOutLiers.shape[0])) / numOfWindows
    MidTermFeaturesNormOr = MidTermFeaturesNorm
    MidTermFeaturesNorm = MidTermFeaturesNorm[:, iNonOutLiers]

    # LDA dimensionality reduction:
    if LDAdim > 0:
        #[mtFeaturesToReduce, _] = aF.mtFeatureExtraction(x, Fs, mtSize * Fs, stWin * Fs, round(Fs*stWin), round(Fs*stWin));
        # extract mid-term features with minimum step:
        mtWinRatio = int(round(mtSize / stWin))
        mtStepRatio = int(round(stWin / stWin))
        mtFeaturesToReduce = []
        numOfFeatures = len(ShortTermFeatures)
        numOfStatistics = 2
        #for i in range(numOfStatistics * numOfFeatures + 1):
        for i in range(numOfStatistics * numOfFeatures):
            mtFeaturesToReduce.append([])

        for i in range(numOfFeatures):        # for each of the short-term features:
            curPos = 0
            N = len(ShortTermFeatures[i])
            while (curPos < N):
                N1 = curPos
                N2 = curPos + mtWinRatio
                if N2 > N:
                    N2 = N
                curStFeatures = ShortTermFeatures[i][N1:N2]
                mtFeaturesToReduce[i].append(numpy.mean(curStFeatures))
                mtFeaturesToReduce[i+numOfFeatures].append(numpy.std(curStFeatures))
                curPos += mtStepRatio
        mtFeaturesToReduce = numpy.array(mtFeaturesToReduce)
        mtFeaturesToReduce2 = numpy.zeros((mtFeaturesToReduce.shape[0] + len(classNames1) + len(classNames2), mtFeaturesToReduce.shape[1]))
        for i in range(mtFeaturesToReduce.shape[1]):
            curF1 = (mtFeaturesToReduce[:, i] - MEAN1) / STD1
            curF2 = (mtFeaturesToReduce[:, i] - MEAN2) / STD2
            [Result, P1] = aT.classifierWrapper(Classifier1, "knn", curF1)
            [Result, P2] = aT.classifierWrapper(Classifier2, "knn", curF2)
            mtFeaturesToReduce2[0:mtFeaturesToReduce.shape[0], i] = mtFeaturesToReduce[:, i]
            mtFeaturesToReduce2[mtFeaturesToReduce.shape[0]:mtFeaturesToReduce.shape[0] + len(classNames1), i] = P1 + 0.0001
            mtFeaturesToReduce2[mtFeaturesToReduce.shape[0]+len(classNames1)::, i] = P2 + 0.0001
        mtFeaturesToReduce = mtFeaturesToReduce2
        mtFeaturesToReduce = mtFeaturesToReduce[iFeaturesSelect, :]
        #mtFeaturesToReduce += numpy.random.rand(mtFeaturesToReduce.shape[0], mtFeaturesToReduce.shape[1]) * 0.0000010
        (mtFeaturesToReduce, MEAN, STD) = aT.normalizeFeatures([mtFeaturesToReduce.T])
        mtFeaturesToReduce = mtFeaturesToReduce[0].T
        #DistancesAll = numpy.sum(distance.squareform(distance.pdist(mtFeaturesToReduce.T)), axis=0)
        #MDistancesAll = numpy.mean(DistancesAll)
        #iNonOutLiers2 = numpy.nonzero(DistancesAll < 3.0*MDistancesAll)[0]
        #mtFeaturesToReduce = mtFeaturesToReduce[:, iNonOutLiers2]
        Labels = numpy.zeros((mtFeaturesToReduce.shape[1], ));
        LDAstep = 1.0
        LDAstepRatio = LDAstep / stWin
        #print LDAstep, LDAstepRatio
        for i in range(Labels.shape[0]):
            Labels[i] = int(i*stWin/LDAstepRatio);        
        clf = sklearn.discriminant_analysis.LinearDiscriminantAnalysis(n_components=LDAdim)
        clf.fit(mtFeaturesToReduce.T, Labels)
        MidTermFeaturesNorm = (clf.transform(MidTermFeaturesNorm.T)).T

    if numOfSpeakers <= 0:
        sRange = range(2, 10)
    else:
        sRange = [numOfSpeakers]
    clsAll = []
    silAll = []
    centersAll = []
    
    for iSpeakers in sRange:        
        k_means = sklearn.cluster.KMeans(n_clusters = iSpeakers)
        k_means.fit(MidTermFeaturesNorm.T)
        cls = k_means.labels_        
        means = k_means.cluster_centers_

        # Y = distance.squareform(distance.pdist(MidTermFeaturesNorm.T))
        clsAll.append(cls)
        centersAll.append(means)
        silA = []; silB = []
        for c in range(iSpeakers):                                # for each speaker (i.e. for each extracted cluster)
            clusterPerCent = numpy.nonzero(cls==c)[0].shape[0] / float(len(cls))
            if clusterPerCent < 0.020:
                silA.append(0.0)
                silB.append(0.0)
            else:
                MidTermFeaturesNormTemp = MidTermFeaturesNorm[:,cls==c]            # get subset of feature vectors
                Yt = distance.pdist(MidTermFeaturesNormTemp.T)                # compute average distance between samples that belong to the cluster (a values)
                silA.append(numpy.mean(Yt)*clusterPerCent)
                silBs = []
                for c2 in range(iSpeakers):                        # compute distances from samples of other clusters
                    if c2!=c:
                        clusterPerCent2 = numpy.nonzero(cls==c2)[0].shape[0] / float(len(cls))
                        MidTermFeaturesNormTemp2 = MidTermFeaturesNorm[:,cls==c2]
                        Yt = distance.cdist(MidTermFeaturesNormTemp.T, MidTermFeaturesNormTemp2.T)
                        silBs.append(numpy.mean(Yt)*(clusterPerCent+clusterPerCent2)/2.0)
                silBs = numpy.array(silBs)                            
                silB.append(min(silBs))                            # ... and keep the minimum value (i.e. the distance from the "nearest" cluster)
        silA = numpy.array(silA); 
        silB = numpy.array(silB); 
        sil = []
        for c in range(iSpeakers):                                # for each cluster (speaker)
            sil.append( ( silB[c] - silA[c]) / (max(silB[c],  silA[c])+0.00001)  )        # compute silhouette

        silAll.append(numpy.mean(sil))                                # keep the AVERAGE SILLOUETTE

    #silAll = silAll * (1.0/(numpy.power(numpy.array(sRange),0.5)))
    imax = numpy.argmax(silAll)                                    # position of the maximum sillouette value
    nSpeakersFinal = sRange[imax]                                    # optimal number of clusters

    # generate the final set of cluster labels
    # (important: need to retrieve the outlier windows: this is achieved by giving them the value of their nearest non-outlier window)
    cls = numpy.zeros((numOfWindows,))
    for i in range(numOfWindows):
        j = numpy.argmin(numpy.abs(i-iNonOutLiers))        
        cls[i] = clsAll[imax][j]
        
    # Post-process method 1: hmm smoothing
    for i in range(1):
        startprob, transmat, means, cov = trainHMM_computeStatistics(MidTermFeaturesNormOr, cls)
        hmm = hmmlearn.hmm.GaussianHMM(startprob.shape[0], "diag")            # hmm training        
        hmm.startprob_ = startprob
        hmm.transmat_ = transmat            
        hmm.means_ = means; hmm.covars_ = cov
        cls = hmm.predict(MidTermFeaturesNormOr.T)                    
    
    # Post-process method 2: median filtering:
    cls = scipy.signal.medfilt(cls, 13)
    cls = scipy.signal.medfilt(cls, 11)

    sil = silAll[imax]                                        # final sillouette
    classNames = ["speaker{0:d}".format(c) for c in range(nSpeakersFinal)];


    # load ground-truth if available
    gtFile = fileName.replace('.wav', '.segments');                            # open for annotated file
    if os.path.isfile(gtFile):                                    # if groundturh exists
        [segStart, segEnd, segLabels] = readSegmentGT(gtFile)                    # read GT data
        flagsGT, classNamesGT = segs2flags(segStart, segEnd, segLabels, mtStep)            # convert to flags

    if PLOT:
        fig = plt.figure()    
        if numOfSpeakers>0:
            ax1 = fig.add_subplot(111)
        else:
            ax1 = fig.add_subplot(211)
        ax1.set_yticks(numpy.array(range(len(classNames))))
        ax1.axis((0, Duration, -1, len(classNames)))
        ax1.set_yticklabels(classNames)
        ax1.plot(numpy.array(range(len(cls)))*mtStep+mtStep/2.0, cls)

    if os.path.isfile(gtFile):
        if PLOT:
            ax1.plot(numpy.array(range(len(flagsGT)))*mtStep+mtStep/2.0, flagsGT, 'r')
        purityClusterMean, puritySpeakerMean = evaluateSpeakerDiarization(cls, flagsGT)
        print "{0:.1f}\t{1:.1f}".format(100*purityClusterMean, 100*puritySpeakerMean)
        if PLOT:
            plt.title("Cluster purity: {0:.1f}% - Speaker purity: {1:.1f}%".format(100*purityClusterMean, 100*puritySpeakerMean) )
    if PLOT:
        plt.xlabel("time (seconds)")
        #print sRange, silAll    
        if numOfSpeakers<=0:
            plt.subplot(212)
            plt.plot(sRange, silAll)
            plt.xlabel("number of clusters");
            plt.ylabel("average clustering's sillouette");
        plt.show()
    return cls


# In[5]:

#input_path = "C:/DiesUndDas/Programmierkram/Python/roboy/roboytestfiles/two_talking/two_talking_after_another_channel_1.wav"
#input_path = "C:/DiesUndDas/Programmierkram/Python/roboy/roboytestfiles/random_internet_dialog_channel_1.wav"
#input_path = "C:/Users/kathi/Documents/4.Semester/roboy/mic_0_two_people.wav"
#input_path = "C:/Users/kathi/Documents/4.Semester/roboy/anne_karin_.wav"  
#input_path = "C:/Users/kathi/Documents/4.Semester/roboy/sgdialog1.wav"
#input_path = "C:/Users/kathi/Documents/4.Semester/roboy/two_women.wav"
input_path = "C:/Users/kathi/Documents/4.Semester/roboy/demo.wav"



#def speakerDiarization(fileName, numOfSpeakers, mtSize=2.0, mtStep=0.2, stWin=0.05, LDAdim=35, PLOT=False):
result = speakerDiarization(input_path, 2)

#result is an array, were each entry represent who is speaking in the current 200ms


# In[ ]:







# In[6]:

result


# In[7]:

def try_sound(chunk,array,label_speaker1,label_speaker2):
    '''function to update gui window and play the wav file 
    '''
    data = f.readframes(chunk)  #####????????????????????????
    #count=0
    start_time = time.time()
    index_array=0
    while(data):
        #data = f.readframes(chunk)  
        stream.write(data)
        #label_speaker1.after(200, which_speaker,data,chunk,f)
        #try:
        time_diff=abs(start_time-time.time()) #calculate duration of while loop iteration
        if time_diff>=0.2*(index_array+1):# an richtiger stelle im array nachschauen ->
            if array[index_array]==0:
                label_speaker1.config(fg="red")
                #label_speaker1.set(label_speaker.get().upper())
                label_speaker2.config(fg="grey")
               # print 'speaker 1'
                top.update()
            elif array[index_array]==1:
                label_speaker1.config(fg="grey")
                label_speaker2.config(fg="red")
               # print 'speaker 2'
                top.update()
            else:
                print 'something weird is happening'
            
            progress['value']=(float(600)/(float(len(array))))*(float(index_array))
            #print (float(array.size)/float(600))*(100*index_array)
            top.update_idletasks()
            index_array+=1

        #count += 1
        #except:
         #   print'input array too short for auudio stream'
            
        #time.sleep(5)
        data = f.readframes(chunk) 
        
    #progress.stop()    
    #stop stream  
    stream.stop_stream()  
    stream.close()  

    #close PyAudio  
    p.terminate() 


# In[ ]:




# In[23]:

#define stream chunk   
chunk = 2000  

#open a wav format music  
#f = wave.open("C:/Users/kathi/Documents/4.Semester/roboy/mic_0_two_people.wav","rb")  
#f = wave.open("C:/Users/kathi/Documents/4.Semester/roboy/anne_karin_.wav","rb") 
#f = wave.open("C:/Users/kathi/Documents/4.Semester/roboy/sgdialog.wav","rb")  
#f = wave.open("C:/Users/kathi/Documents/4.Semester/roboy/two_women.wav","rb")  
f = wave.open("C:/Users/kathi/Documents/4.Semester/roboy/demo.wav","rb")  


#instantiate PyAudio  
p = pyaudio.PyAudio()  
#open stream  
stream = p.open(format = p.get_format_from_width(f.getsampwidth()),  
                channels = f.getnchannels(),  
                rate = f.getframerate(),  
                output = True)  
#read data  
data = f.readframes(chunk)  





######creating gui window here 

top = tk.Toplevel()

top.title("Who is speaking?")
#top.configure(background='black')
frame = tk.Frame(top)
frame.pack()
top.geometry("700x300")
top.pack_propagate(0)

progress=ttk.Progressbar(top,orient=tk.HORIZONTAL,length=600,maximum=600,mode='determinate')
progress.pack()
#progress['maximum']=600
img=tk.PhotoImage(file="roboy.gif")
#img=img.zoom(25)
img=img.subsample(2)
panel = tk.Label(top, image = img)
#panel.pack(side = "left")#, fill = "both", expand = "yes")
panel.pack()


label_speaker1 = tk.Label(top, fg="dark red")
label_speaker1.pack(padx=5, pady=10, side=tk.LEFT)
label_speaker1.config(text='speaker 1',width=20)
label_speaker1.config(font=("Courier", 20))


label_speaker2 = tk.Label(top, fg="dark red")
label_speaker2.pack(padx=5, pady=10, side=tk.LEFT)
label_speaker2.config(text='speaker 2',width=20)
label_speaker2.config(font=("Courier", 20))


#img=plt.imread('test.png')
#plt.imshow(img)
#panel = tk.Label(top, image = img)
#panel.pack(side = "bottom", fill = "both", expand = "yes")

try_sound(chunk,result,label_speaker1,label_speaker2)
top.update()


top.mainloop()


# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:



