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
import sys

def load_sample_file(sample_file):
	f= open(sample_file, "r")
	Fs = pickle.load(f)
	x = pickle.load(f)
	speaker_id=pickle.load(f)
	print Fs
	print x
	print speaker_id
	f.close()
	return Fs,x,speaker_id

def save_model_in_file(gmm,speaker_id,speaker_name):	
	f = open('train_models/'+speaker_name+'.txt', "w")
	pickle.dump(gmm, f)
	pickle.dump(speaker_id,f)
	pickle.dump(speaker_name,f)
	f.close()
	
if __name__=="__main__":

	use_folder_for_training=False

	if len(sys.argv) != 2 or len(sys.argv)!=1:
		print 'amount of sys.argv has to be 1 or 0, first is txt file, countaing fs,x,speaker_id you want to train, if 0 folder train_data is used for training'
		#break
		#######TODO: beende programm hiere!!
		
	
	if len(sys.argv) ==1:
		use_folder_for_training = True
		print 'in one'
	else:
		training_file_name=sys.argv[1]
		
	
		

	window = 0.020
	window_overlap = 0.010
	voiced_threshold_mul = 0.05
	voiced_threshold_range=100
	n_mixtures = 128
	max_iterations = 75
	calc_deltas=True


	#speakers={}
	
	
	if not use_folder_for_training:
		Fs,x,speaker_id=load_sample_file(training_file_name)
		print training_file_name
		speaker_name=training_file_name.replace('.txt','')
		print speaker_name
		features = MFCC_extractor.extract_MFCCs(x,Fs,window*Fs,window_overlap*Fs,voiced_threshold_mul,voiced_threshold_range,calc_deltas)
		gmm = mixture.GaussianMixture(n_components=n_mixtures, covariance_type='diag' , max_iter = max_iterations ).fit(features)
		save_model_in_file(gmm,speaker_id,speaker_name)
	else: 
		######delete all models that are still in the train_models folder
		if len(glob.glob('train_models/*'))>0:
			for f in glob.glob('train_models/*'):
				os.remove(f)
		spct=0
		total_sp=len(glob.glob('train_wavdata/*'))	
		for speaker in sorted(glob.glob('train_wavdata/*')):
			print (spct/float(total_sp))*100.0,'% completed'
			#print speaker
			###### speaker_name should get rid of the folder name, but it doesnt work 
			speaker_name=speaker.replace('train_wavdata','')
			#print speaker_name
			#speakers.update({speaker_name:spct})
			
			all_speaker_Fs,all_speaker_data=0,[]
			####### if there are more then one trainig file for one speaker, train all
			for sample_file in glob.glob(speaker+'/*.txt'):
				####### read the pickled np arrays 
				print sample_file
				Fs,x,speaker_id=load_sample_file(sample_file)
				if all_speaker_Fs==0:	all_speaker_Fs=Fs

				if Fs==all_speaker_Fs:
					features = MFCC_extractor.extract_MFCCs(x,Fs,window*Fs,window_overlap*Fs,voiced_threshold_mul,voiced_threshold_range,calc_deltas)
					if len(all_speaker_data)==0:	all_speaker_data=features
					else:							all_speaker_data=np.concatenate((all_speaker_data,features),axis=0)
				else:	print sample_file+" skipped due to mismatch in frame rate"
			#try:
			gmm = mixture.GaussianMixture(n_components=n_mixtures, covariance_type='diag' , max_iter = max_iterations ).fit(all_speaker_data)
			#except:
				#print "ERROR : Error while training model for file "+speaker
			save_model_in_file(gmm,speaker_id,speaker_name)
			
			spct+=1
			print 'training done for speaker: '+ speaker_name + ' with speaker_id' + str(speaker_id)
			
		
	print 'training done '


