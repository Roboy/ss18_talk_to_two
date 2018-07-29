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
	#print Fs
	#print x
	#print speaker_id
	f.close()
	return Fs,x,speaker_id

def load_mode_file(model_file):
	f=open(model_file,"r")
	gmm = pickle.load(f)
	speaker_id = pickle.load(f)
	speaker_name=pickle.load(f)
	f.close()
	return gmm,speaker_id,speaker_name
	
def check_which_model_fits_best_to_test_file(features,speaker_id_test_file):
	max_score=-9999999
	max_speaker=9999
	for modelfile in sorted(glob.glob('train_models/*.txt')):
		gmm,speaker_id,speaker_name=load_mode_file(modelfile)
		score=gmm.score(features)
		#print score
		if score>max_score:
			max_score,max_speaker=score,speaker_id
	print 'correct speaker: '+str(speaker_id_test_file)+" -> "+ 'what model believes:  '+str(max_speaker)+(" Y" if speaker_id_test_file==max_speaker  else " N")
	

	
if __name__=="__main__":

	use_folder_for_testing=False

	if len(sys.argv) != 3 or len(sys.argv)!=1:
		print 'amount of sys.argv has to be 2 or 0, first is txt file, containg fs,x,speaker_id you want to test; if 0 folder train_data is used for training'
		#break
		#######TODO: beende programm hiere!!
		
	
	if len(sys.argv) ==1:
		use_folder_for_testing = True
		print 'in one'
	else:
		testing_file_name=sys.argv[1]


	window = 0.020
	window_overlap = 0.010
	voiced_threshold_mul = 0.05
	voiced_threshold_range=100
	n_mixtures = 128
	max_iterations = 75
	calc_deltas=True


	
	if not use_folder_for_testing:
		print testing_file_name
		Fs,x,speaker_id_test_file=load_sample_file(testing_file_name)
		features = MFCC_extractor.extract_MFCCs(x,Fs,window*Fs,window_overlap*Fs,voiced_threshold_mul,voiced_threshold_range,calc_deltas)
		check_which_model_fits_best_to_test_file(features,speaker_id_test_file)
	
	else: 
		spct=0
		total_sp=len(glob.glob('train_wavdata/*'))
		#confusion_matrix = np.zeros((total_sp,total_sp))
		tct=0
	
		for testcasefile in glob.glob('test_wavdata'+'/*.txt'):
			print testcasefile
			Fs,x,speaker_id_test_file=load_sample_file(testcasefile)
			features = MFCC_extractor.extract_MFCCs(x,Fs,window*Fs,window_overlap*Fs,voiced_threshold_mul,voiced_threshold_range,calc_deltas)
			check_which_model_fits_best_to_test_file(features,speaker_id_test_file)
				#confusion_matrix[ speakers[speaker] ][speakers[max_speaker]]+=1

		#print "Accuracy: ",(sum([ confusion_matrix[i][j] if i==j  else 0 for i in xrange(total_sp) for j in xrange(total_sp) ] )*100)/float(tct*total_sp)'''
