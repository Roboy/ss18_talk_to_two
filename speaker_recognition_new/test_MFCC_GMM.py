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

	

	
if __name__=="__main__":

	use_folder_for_testing=False

	if len(sys.argv) != 2 and len(sys.argv)!=1:
		print 'amount of sys.argv has to be 1 or 0, first is txt file, containg fs,x,speaker_id you want to test; if 0 folder train_data is used for training'
		sys.exit(0)
		
	
	if len(sys.argv) ==1:
		use_folder_for_testing = True
		#sprint 'in one'
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
		Fs,x,speaker_id_test_file=hf.load_sample_file(testing_file_name)
		features = MFCC_extractor.extract_MFCCs(x,Fs,window*Fs,window_overlap*Fs,voiced_threshold_mul,voiced_threshold_range,calc_deltas)
		max_speaker=hf.check_which_model_fits_best_to_test_file(features,speaker_id_test_file)
		if speaker_id_test_file != max_speaker:
			print 'Error detected!!'
			#######TODO: what to do when error detected??? new id could be saved or something 
	else: 
		spct=0
		total_sp=len(glob.glob('train_wavdata/*'))
		#confusion_matrix = np.zeros((total_sp,total_sp))
		tct=0
	
		for testcasefile in glob.glob('test_wavdata'+'/*.txt'):
			print testcasefile
			Fs,x,speaker_id_test_file=hf.load_sample_file(testcasefile)
			features = MFCC_extractor.extract_MFCCs(x,Fs,window*Fs,window_overlap*Fs,voiced_threshold_mul,voiced_threshold_range,calc_deltas)
			max_speaker=hf.check_which_model_fits_best_to_test_file(features,speaker_id_test_file)
			print max_speaker
			print speaker_id_test_file
			if speaker_id_test_file != max_speaker:
				print 'Error detected!! '
				#confusion_matrix[ speakers[speaker] ][speakers[max_speaker]]+=1
	print 'testing done'
		#print "Accuracy: ",(sum([ confusion_matrix[i][j] if i==j  else 0 for i in xrange(total_sp) for j in xrange(total_sp) ] )*100)/float(tct*total_sp)'''
