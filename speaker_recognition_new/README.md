# Speaker-Recognition-System-using-GMM
System to identify speaker recognition using MFCC features and GMMs.


you can use save_wav_as_np_array.py to convert wav files into np_arrays and adding a speaker identification number and a name.

train_MFCC_GMM.py takes as input variables either a file to train on or uses the folder train_wavdata to train the GMM, and a bool True if you want to update the GMMs with the new data if there already exists one with the same speaker ID.

test_MFCC_GMM.py takes as input a test_file or uses the folder test_wavdata to test all files.
