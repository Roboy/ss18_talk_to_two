from sklearn.externals import joblib
import glob
import os
from shutil import copyfile
from scipy.fftpack import fft,ifft
import pickle
import MFCC_extractor
import sys
import time



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
	start_time=time.time()
	max_score=-9999999
	max_speaker=9999
	for modelfile in sorted(glob.glob('train_models/*.txt')):
		gmm,speaker_id,speaker_name=load_mode_file(modelfile)
		score=gmm.score(features)
		#print score
		if score>max_score:
			max_score,max_speaker=score,speaker_id
	print 'speaker indicated by test_file: '+str(speaker_id_test_file)+" -> "+ 'what model believes:  '+str(max_speaker)+(" Y" if speaker_id_test_file==max_speaker  else " N")
	print 'testing took '+ str(time.time()-start_time) + ' seconds'
	
	return max_speaker
	
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

def save_model_in_file(gmm,speaker_id,speaker_name):	
	f = open('train_models/'+str(speaker_id)+'.txt', "w")
	pickle.dump(gmm, f)
	pickle.dump(speaker_id,f)
	pickle.dump(speaker_name,f)
	f.close()