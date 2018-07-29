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
	
	######delete all models that are still in the train_models folder
	if len(glob.glob('train_models/train_wavdata/*'))>0:
		for f in glob.glob('train_models/train_wavdata/*'):
			os.remove(f)
			
	for speaker in sorted(glob.glob('train_wavdata/*')):
		print (spct/float(total_sp))*100.0,'% completed'
		print speaker
		###### speaker_name should get rid of the folder name, but it doesnt work 
		speaker_name=speaker.replace('train_wavdata/','_')
		print speaker_name
		#speakers.update({speaker_name:spct})
		
		all_speaker_Fs,all_speaker_data=0,[]
		####### if there are more then one trainig file for one speaker, train all
		for sample_file in glob.glob(speaker+'/*.txt'):
			####### read the pickled np arrays 
			print sample_file
			f= open(sample_file, "r")
			Fs = pickle.load(f)
			x = pickle.load(f)
			speaker_id=pickle.load(f)
			print Fs
			print x
			print speaker_id
			f.close()
			
			
	
			if all_speaker_Fs==0:	all_speaker_Fs=Fs

			if Fs==all_speaker_Fs:
				features = MFCC_extractor.extract_MFCCs(x,Fs,window*Fs,window_overlap*Fs,voiced_threshold_mul,voiced_threshold_range,calc_deltas)
				if len(all_speaker_data)==0:	all_speaker_data=features
				else:							all_speaker_data=np.concatenate((all_speaker_data,features),axis=0)
			else:	print sample_file+" skipped due to mismatch in frame rate"
		#print all_speaker_data
		#try:
		gmm = mixture.GaussianMixture(n_components=n_mixtures, covariance_type='diag' , max_iter = max_iterations ).fit(all_speaker_data)
		#except:
			#print "ERROR : Error while training model for file "+speaker
		
		#try:
		joblib.dump(gmm,'train_models/'+speaker_name+'.pkl')
		#except:
			 #print "ERROR : Error while saving model for "+speaker_name

		spct+=1
		print 'training done for speaker: '+ speaker_name + 'with speaker_id' + str(speaker_id)
		
		
	print 'training done '


