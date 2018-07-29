# Talk to two

This will be the most important stuff regarding this impressive project. It's about beeing able to talk to two people at the same time. And these are the Instructions to make it work.

Speaker diarization is the process of splitting an audio stream into segments according to who is speaking. 
In order to achive this goal this program has the functionality of recognizing at what point of time which speaker is speaking. Before using it you have to specify how many people you want to find in the audio stream.
If you want to read more about the theory and how the program works you find additional information here:
https://ieeexplore.ieee.org/document/6171836/?arnumber=6171836&abstractAccess=no&userType=inst
https://github.com/tyiannak/pyAudioAnalysis/wiki/5.-Segmentation
## Pre-requisites
Speaker diarization is only working in python 2.7 so make sure that you have a running version before you try to install it. And please make sure that you have 
a working python 2.7 environment set up for anaconda. 

You need to make sure that you have some dependencies installed or install them, those are the Linux installing commands, but you can also install everything on windows: 

- NUMPY

pip install numpy

- MATPLOTLIB

pip install matplotlib

- SCIPY

pip install scipy  

- SKLEARN

pip install sklearn 

- hmmlearn

pip install hmmlearn

- Simplejson

pip install simplejson

- eyeD3

pip install eyed3

- pydub

pip install pydub

- pyAudio
pip install pyaudio 

-tkinter
sudo apt-get install python-tk

- tkk

- time 

- wave 


Note: it is possible to make it work on windows but I think running it on ubuntu is easier. 

## How to build

- Clone the git repository to your computer:

git clone https://github.com/Roboy/ss18_talk_to_two.git

- switch to the speaker diarization branch:

git checkout speaker_diarization




## How to test
The speaker diarization is an ipython file that is contained in the folder pyAudioAnalysis which you just cloned from github. 
Copy the wav file you want to analize to the folder input_data which is located in ss18_talk_to_two/pyAudioAnalysis. 
Open the file speaker_diarization_with_visualization.ipynb in anaconda and change the variable "input_file_path" to the name of the file you want to analyze.
Afterwards compile and run the whole file. 

## How to use
