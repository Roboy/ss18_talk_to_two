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
import helpful_functions as hf
import time


	
def look_for_existing_model_for_speaker(speaker_id_given):
	for modelfile in sorted(glob.glob('train_models/*.txt')):
		print modelfile
		gmm,speaker_id,speaker_name=hf.load_mode_file(modelfile)
		if speaker_id==speaker_id_given:
			print 'gmm found and returned'
			return gmm
	return 0

def update_model_if_existing(speaker_id_given,features):
	gmm=look_for_existing_model_for_speaker(speaker_id)
	print gmm
	if gmm !=0:
		gmm.fit(features)
		print 'existing model updated'
	else:
		print 'no existing model, creating a new one '
		gmm = mixture.GaussianMixture(n_components=n_mixtures, covariance_type='diag' , max_iter = max_iterations ).fit(features)
	return gmm
	
def set_update_model(str):
	if str == 'True' or str == 'true':
		return True
	elif str == 'False' or str == 'false' or str =='FALSE':
		return False
	else:
		print 'update model variable not readable'
		sys.exit(0)
	
if __name__=="__main__":

	use_folder_for_training=False

	if len(sys.argv) != 3 and len(sys.argv)!=2:
		print 'ERROR: amount of sys.argv has to be 1 or 0, first is txt file, countaing fs,x,speaker_id you want to train,second is bool if you want to date model up or train completely new, if 0 folder train_data is used for training'
		sys.exit(0)
		
	
	if len(sys.argv) ==2:
		use_folder_for_training = True
		update_model=set_update_model(sys.argv[1])
		#update_model=sys.argv[1]
		print 'in one'
	else:
		training_file_name=sys.argv[1]
		update_model=set_update_model(sys.argv[2])
		#update_model=sys.argv[2]
		
	
		

	window = 0.020
	window_overlap = 0.010
	voiced_threshold_mul = 0.05
	voiced_threshold_range=100
	n_mixtures = 128
	max_iterations = 75
	calc_deltas=True


	#speakers={}
	
	
	if not use_folder_for_training:
		start_time=time.time()
		Fs,x,speaker_id=hf.load_sample_file(training_file_name)
		#print training_file_name
		speaker_name=training_file_name.replace('.txt','')
		#print speaker_name
		features = MFCC_extractor.extract_MFCCs(x,Fs,window*Fs,window_overlap*Fs,voiced_threshold_mul,voiced_threshold_range,calc_deltas)
		print update_model
		if update_model:
			print 'in updating model'
			gmm = update_model_if_existing(speaker_id,features)
		else:
			print 'model trained without changing existing models if there are some'
			gmm = mixture.GaussianMixture(n_components=n_mixtures, covariance_type='diag' , max_iter = max_iterations ).fit(features)
		hf.save_model_in_file(gmm,speaker_id,speaker_name)
		print 'training took '+str (time.time()-start_time)+ ' for the one training file'
	
	else: 
		speaker_count=0
		start_time=time.time()
		if not update_model:
			######delete all models that are still in the train_models folder
			if len(glob.glob('train_models/*'))>0:
				for f in glob.glob('train_models/*'):
					os.remove(f)
				
		#print update_model		
		spct=0
		total_sp=len(glob.glob('train_wavdata/*'))	
		for speaker in sorted(glob.glob('train_wavdata/*')):
			print (spct/float(total_sp))*100.0,'% completed'
			speaker_name=speaker.replace('train_wavdata','')

			all_speaker_Fs,all_speaker_data=0,[]
			####### if there are more then one trainig file for one speaker, train all
			for sample_file in glob.glob(speaker+'/*.txt'):
				####### read the pickled np arrays 
				#print sample_file
				Fs,x,speaker_id=hf.load_sample_file(sample_file)
				if all_speaker_Fs==0:	all_speaker_Fs=Fs

				if Fs==all_speaker_Fs:
					features = MFCC_extractor.extract_MFCCs(x,Fs,window*Fs,window_overlap*Fs,voiced_threshold_mul,voiced_threshold_range,calc_deltas)
					if len(all_speaker_data)==0:	all_speaker_data=features
					else:							all_speaker_data=np.concatenate((all_speaker_data,features),axis=0)
				else:	print sample_file+" skipped due to mismatch in frame rate"
			#print update_model
			if update_model:
				print 'training whole folder, updating existing models if there are some'
				gmm = update_model_if_existing(speaker_id,all_speaker_data)
			else:
				print 'training whole folder, model trained without changing existing models if there are some'
				gmm = mixture.GaussianMixture(n_components=n_mixtures, covariance_type='diag' , max_iter = max_iterations ).fit(all_speaker_data)
			hf.save_model_in_file(gmm,speaker_id,speaker_name)
			
			spct+=1
			print 'training done for speaker: '+ speaker_name + ' with speaker_id' + str(speaker_id)
			speaker_count+=1	
		print 'training took '+str (time.time()-start_time)+ ' for '+ str(speaker_count)+  '  speakers'
		
	print 'training done '


