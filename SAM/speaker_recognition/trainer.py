import threading
import MFCC_extractor
from sklearn import mixture
import copy
import time 


class Trainer (threading.Thread):
	def __init__(self,latest_id_to_train,latest_audio_to_train,gmm_models,trainer_gmm_queue):
		threading.Thread.__init__(self)
		self.window = 0.020
		self.window_overlap = 0.010
		self.voiced_threshold_mul = 0.05
		self.voiced_threshold_range=100
		self.n_mixtures = 128
		self.max_iterations = 75
		self.calc_deltas=True
		self.Fs=16000
		self.latest_id_to_train=latest_id_to_train
		self.latest_audio_to_train=latest_audio_to_train
		self.trainer_gmm_queue=trainer_gmm_queue
		self.gmm_models=gmm_models
		
	def run(self):
			#print 'run trainer'
			start_time=time.time()
			features = MFCC_extractor.extract_MFCCs(self.latest_audio_to_train,self.Fs,self.window*self.Fs,self.window_overlap*self.Fs,self.voiced_threshold_mul,self.voiced_threshold_range,self.calc_deltas)
			##### if gmm with latest_id_to_train exists update that model
			#if self.gmm_models[self.latest_id_to_train]:
			#print self.gmm_models
			if self.latest_id_to_train in self.gmm_models:
				old_model=copy.deepcopy(self.gmm_models[self.latest_id_to_train])
				print 'updating existing model'
				#print self.latest_id_to_train
				new_model=old_model.fit(features)
			######else train new one and write it at the right place 
			else: 
				print 'creating new model'
				#print self.latest_id_to_train
				new_model= mixture.GaussianMixture(n_components=self.n_mixtures, covariance_type='diag' , max_iter = self.max_iterations ).fit(features)
			
			self.trainer_gmm_queue.put((self.latest_id_to_train,new_model))
			#print self.latest_id_to_train,new_model
			print 'training took '+str (time.time()-start_time)+ ' for the one training file'
			#print 'trainer is done and closing itself'