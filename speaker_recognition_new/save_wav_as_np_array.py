import numpy as np
from pyAudioAnalysis import audioBasicIO
import pickle
import glob

if __name__=="__main__":
	test_file=True
	speaker_id = 0
	for speaker in sorted(glob.glob('test_wavdata/train_wavdata/*')):
		print speaker
		speaker_name=speaker.replace('test_wavdata/train_wavdata','')
		print speaker_name

		for sample_file in glob.glob(speaker+'/*.wav'):

			[Fs, x] = audioBasicIO.readAudioFile(sample_file)
			print Fs
			print x
			f = open('converted_to_np_arrays/'+speaker_name+'.txt', "w")
			pickle.dump(Fs, f)
			pickle.dump(x, f)
			if not test_file:
				pickle.dump(speaker_id,f)
			f.close()

			'''f= open('converted_to_np_arrays/'+speaker_name, "r")
			Fs1 = pickle.load(f)
			x1 = pickle.load(f)
			speaker_id1=pickle.load(f)
			print Fs
			print x
			print speaker_id1'''
			f.close()
		speaker_id+=1