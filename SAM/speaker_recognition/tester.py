import threading
import MFCC_extractor
from sklearn import mixture
import operator
import time 

class Tester (threading.Thread):
	def __init__(self,audio_to_test,odas_id,outq,gmm_models):
		threading.Thread.__init__(self)
		self.window = 0.020
		self.window_overlap = 0.010
		self.voiced_threshold_mul = 0.05
		self.voiced_threshold_range=100
		self.n_mixtures = 128
		self.max_iterations = 75
		self.calc_deltas=True
		self.Fs=16000
		self.audio_to_test=audio_to_test
		self.odas_id=odas_id
		self.outq=outq
		self.gmm_models=gmm_models
		###### this threshold should be tuned 
		self.threshold=9.53
		
		
		
		
		
		
	def run(self):
		print 'testing new file'
		start_time=time.time()
		#print self.audio_to_test
		features = MFCC_extractor.extract_MFCCs(self.audio_to_test,self.Fs,self.window*self.Fs,self.window_overlap*self.Fs,self.voiced_threshold_mul,self.voiced_threshold_range,self.calc_deltas)
		######check if one model fits well
		max_score=-9999999
		max_speaker=9999
		certainty=10
		scores=dict()
		if len(self.gmm_models)==0:
			certainty=0
			max_speaker=self.odas_id
		else:
			for id in self.gmm_models:
				#print id
				score=self.gmm_models[id].score(features)
				#print score
				scores[id]=score
				if score>max_score:
					max_score,max_speaker=score,id
			
			max_score_key=max(scores.iteritems(), key=operator.itemgetter(1))[0]
			max_score=max(scores.iteritems(), key=operator.itemgetter(1))[1]
			min_score_key=min(scores.iteritems(), key=operator.itemgetter(1))[0]
			min_score=min(scores.iteritems(), key=operator.itemgetter(1))[1]

			
			###### calculate diference to see if it's a new speaker, still needs some tuning 
			print 'dif '+str(abs(max_score-min_score))
			if abs(max_score-min_score)<self.threshold and abs(max_score-min_score)!=0:
				print 'new speaker'
				max_speaker=-99
				###### adjust certainty
				certainty=5
			
		self.outq.put((self.odas_id, max_speaker, certainty))
		print 'speaker ', str(max_speaker), ' recognized with certainty  ', certainty

		print 'testing took '+str (time.time()-start_time)+ ' for the one test file'
		
		
		