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

def extract_MFCCs(x,Fs,window_size,overlap,VTH_Multiplier=0.05,VTH_range=100,deltas=False):
	
	energy = [ s**2 for s in x]
	Voiced_Threshold = VTH_Multiplier*np.mean(energy)
	clean_samples=[0]
	
	for sample_set in xrange(0,len(x)-VTH_range,VTH_range):
		sample_set_th = np.mean(energy[sample_set:sample_set+VTH_range])
		if sample_set_th>Voiced_Threshold:
			clean_samples.extend(x[sample_set:sample_set+VTH_range])

	energy=None

	#try:
	MFCC13_F = AFE.stFeatureExtraction(clean_samples, Fs, window_size, overlap)
	#except:
	#	print "ERROR:extract_MFCCs: Error while trying to extract mfccs"
	#	return []
	#print MFCC13_F
	clean_samples=None

	if not deltas:
		return MFCC13_F
	
	delta_MFCC = np.zeros(MFCC13_F.shape)
	for t in range(delta_MFCC.shape[1]):
		index_t_minus_one,index_t_plus_one=t-1,t+1
		
		if index_t_minus_one<0:    
			index_t_minus_one=0
		if index_t_plus_one>=delta_MFCC.shape[1]:
			index_t_plus_one=delta_MFCC.shape[1]-1
		
		delta_MFCC[:,t]=0.5*(MFCC13_F[:,index_t_plus_one]-MFCC13_F[:,index_t_minus_one] )
	
	
	double_delta_MFCC = np.zeros(MFCC13_F.shape)
	for t in range(double_delta_MFCC.shape[1]):
		
		index_t_minus_one,index_t_plus_one, index_t_plus_two,index_t_minus_two=t-1,t+1,t+2,t-2
		
		if index_t_minus_one<0:
			index_t_minus_one=0
		if index_t_plus_one>=delta_MFCC.shape[1]:
			index_t_plus_one=delta_MFCC.shape[1]-1
		if index_t_minus_two<0:
			index_t_minus_two=0
		if index_t_plus_two>=delta_MFCC.shape[1]:
			index_t_plus_two=delta_MFCC.shape[1]-1
		  
		double_delta_MFCC[:,t]=0.1*( 2*MFCC13_F[:,index_t_plus_two]+MFCC13_F[:,index_t_plus_one]
									-MFCC13_F[:,index_t_minus_one]-2*MFCC13_F[:,index_t_minus_two] )
	
	Combined_MFCC_F = np.concatenate((MFCC13_F,delta_MFCC,double_delta_MFCC),axis=1)
	
	return Combined_MFCC_F
	