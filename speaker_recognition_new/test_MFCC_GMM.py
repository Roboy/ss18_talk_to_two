import numpy as np
from pyAudioAnalysis import audioBasicIO
import Audio_Feature_Extraction as AFE
from sklearn import mixture
from sklearn.externals import joblib
import glob
import os
from shutil import copyfile
from scipy.fftpack import fft,ifft
import pickle
import MFCC_extractor


if __name__=="__main__":

	window = 0.020
	window_overlap = 0.010
	voiced_threshold_mul = 0.05
	voiced_threshold_range=100
	n_mixtures = 128
	max_iterations = 75
	calc_deltas=True


	#speakers={}
	spct=0
	total_sp=len(glob.glob('train_wavdata/*'))
	confusion_matrix = np.zeros((total_sp,total_sp))
	tct=0
	
	####### sprecher id muss ins modell mit eingespeichert werden!! das hier ist schmarrn 
	#for speaker in speakers:
	for speaker in sorted(glob.glob('train_wavdata/*')):###### check if its close to one of the trained speakers
		print speaker
		#speaker_name=speaker.replace('test_wavdata/train_wavdata','')
		#print speaker_name
		if tct<=0:
			tct=len(glob.glob('test_wavdata/train_wavdata'+'/*.txt'))
		for testcasefile in glob.glob('test_wavdata/train_wavdata'+'/*.txt'):
			f= open(testcasefile, "r")
			Fs = pickle.load(f)
			x = pickle.load(f)
			#speaker_id=pickle.load(f)
			print Fs
			print x
			#print speaker_id
			f.close()
			features = MFCC_extractor.extract_MFCCs(x,Fs,window*Fs,window_overlap*Fs,voiced_threshold_mul,voiced_threshold_range,calc_deltas)
			max_score=-9999999
			max_speaker=speaker
			for modelfile in sorted(glob.glob('train_models/*.pkl')):
				gmm = joblib.load(modelfile) 
				score=gmm.score(features)
				if score>max_score:
					max_score,max_speaker=score,modelfile.replace('train_models_given/','').replace('.pkl','')
			print speaker+" -> "+max_speaker+(" Y" if speaker==max_speaker  else " N")
			#confusion_matrix[ speakers[speaker] ][speakers[max_speaker]]+=1

	#print "Accuracy: ",(sum([ confusion_matrix[i][j] if i==j  else 0 for i in xrange(total_sp) for j in xrange(total_sp) ] )*100)/float(tct*total_sp)'''
