import numpy as np
from pyAudioAnalysis import audioBasicIO
import pickle
import glob

if __name__=="__main__":
	test_file=False
	speaker_id = 0
	for speaker in sorted(glob.glob('wav_data/*')):
		print speaker
		speaker_name=speaker.replace('wav_data','')
		print speaker_name
		#speaker_name=speaker.replace('/','')
		#print speaker_name

		for sample_file in glob.glob(speaker+'/*.wav'):
			print sample_file
			sample_file_name=sample_file.replace('wav_data','')
			sample_file_name=sample_file_name.replace(speaker_name,'')
			sample_file_name=sample_file_name.replace('.wav','')
			print sample_file_name
			[Fs, x] = audioBasicIO.readAudioFile(sample_file)
			print Fs
			print x
			f = open('converted_to_np_arrays/'+sample_file_name+'.txt', "w")
			pickle.dump(Fs, f)
			pickle.dump(x, f)
			if not test_file:
				pickle.dump(speaker_id,f)
				print speaker_id
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