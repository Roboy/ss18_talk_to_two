import trainer as tr
import tester as te
from Queue import Queue
from Queue import Empty
import threading
import helpful_functions as hf 
import glob


class Speaker_recognition(threading.Thread):
	
	def __init__(self):
		#self.all_trainer=[]
		#self.all_tester=[]
		threading.Thread.__init__(self)
		self.gmm_models=dict()
		self.tester_queue=Queue(maxsize=1000)
		self.trainer_queue=Queue(maxsize=1000)
		self.tester_id_queue=Queue(maxsize=1000)
		self.trainer_gmm_queue=Queue(maxsize=1000)
		self.please_stop=threading.Event()
		
		
	def train(self,odas_id,train_audio):
		#while not self.please_stop.set():
		
		###### check if we have to call a tester 
		#TODO: handle an empty gmm_models 
		'''odas_id,latest_audio_to_test=self.tester_queue.get(block=False)
		tester=te.Tester()
		tester.start(odas_id,latest_audio_to_test,self.gmm_models,self.tester_id_queue)
		print 'testing done'''
		
		######odas was sure about which speaker is speaking in the audio file, we can directly train on it 
		

		trainer=tr.Trainer(odas_id,train_audio,self.gmm_models,self.trainer_gmm_queue)
		trainer.run()
		#print 'training done'
		
		####### update self.gmm_models with all models that are in queue 
		id=None
		print 'starting updating gmm_models'
		try:
			id,gmm_model=self.trainer_gmm_queue.get(block=True) 
			#print id, gmm_model
		except Empty:
			print 'Empty found'
			#break
			pass
		if id !=None:
			#print id
			#print gmm_model
			self.gmm_models[id]=gmm_model
			#print self.gmm_models
		
		#self.stop()
		
	
	
	def test(self,audio_to_test,odas_id,outq):
		print 'in test'
		tester=te.Tester(audio_to_test,odas_id,outq,self.gmm_models)
		tester.run()
		
		
	
	
	
			
	def stop(self):
		self.please_stop.set()		
			
if __name__ == "__main__":
    
    #Fs,x,speaker_id=hf.load_sample_file('Jonas_other.txt')
    sr=Speaker_recognition()
    #sr.trainer_queue.put((speaker_id,x))
    queue=Queue(maxsize=1000)
    #print sr.trainer_queue
    #sr.train()
    #ssr.test(x,speaker_id,queue)
	
    for speaker in sorted(glob.glob('train_wavdata/*')):
			#print (spct/float(total_sp))*100.0,'% completed'
			speaker_name=speaker.replace('train_wavdata','')

			all_speaker_Fs,all_speaker_data=0,[]
			####### if there are more then one trainig file for one speaker, train all
			for sample_file in glob.glob(speaker+'/*.txt'):
				####### read the pickled np arrays 
				#print sample_file
				Fs,x,speaker_id=hf.load_sample_file(sample_file)
				#sr.trainer_queue.put((speaker_id,x))
				sr.train(speaker_id,x)
    sr.train(speaker_id,x)
    #print sr.trainer_queue
	#sr.train()
    #print sr.gmm_models
	
    #trainer1=tr.Trainer(speaker_id,x,sr.gmm_models,sr.trainer_gmm_queue)
    #trainer1.train()
    #trainer2=tr.Trainer(speaker_id,x,sr.gmm_models,sr.trainer_gmm_queue)
    #trainer2.train()
	
    #print sr.trainer_gmm_queue.get(block=False)
	
    for testcasefile in glob.glob('test_wavdata'+'/*.txt'):
		print testcasefile
		Fs,x,speaker_id_test_file=hf.load_sample_file(testcasefile)
		print x, speaker_id_test_file
		sr.test(x,speaker_id_test_file,queue)
    
			
		
		
		
		
		
	
		
		