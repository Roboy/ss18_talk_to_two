# Speaker Diarization

This will be the most important stuff regarding this impressive project. It's about beeing able to talk to two people at the same time. And these are the Instructions to make it work.

Speaker diarization is the process of splitting an audio stream into segments according to who is speaking.
In order to achive this goal this program has the functionality of recognizing at what point of time which speaker is speaking. Before using it you have to specify how many people you want to find in the audio stream.The big downside is that it's not working on real time. You load a .wav file after recording it and then have it analysed.

If you want to read more about the theory and how the program works you find additional information here:
- [Fisher Linear Semi-Discriminant Analysis for Speaker Diarization](https://ieeexplore.ieee.org/document/6171836/?arnumber=6171836&abstractAccess=no&userType=inst)
- [pyAudioAnalysis-Segmentation](https://github.com/tyiannak/pyAudioAnalysis/wiki/5.-Segmentation)


## Pre-requisites
Speaker diarization is an ipython notebook running only in python 2.7, so please make sure that you have a working python 2.7 anaconda environment set up and a program that can run ipython notebooks e.g. anaconda before you continue.

If you don't have a working python 2.7 anaconda environment you can check out this page [Conda User Guide](https://conda.io/docs/user-guide/tasks/manage-python.html) or follow these steps:
- make a new 2.7 environment in anaconda:

      conda create -n <environment_name> pythone=2.7 anaconda

- activate your environment:

      source activate <environment_name>

- verify that you are running python 2.7

      python --version

    expected printout (or a similar one):

      python 2.7.15::Anaconda custom (64-bit)

If you don't have a jupyter notbook reader check out this [installation guide](http://jupyter.readthedocs.io/en/latest/install.html)  





You need to make sure that you have some dependencies installed or install them. Those are the Linux installing commands, but you can also install everything on windows:


- NUMPY

      conda install numpy

- MATPLOTLIB

      conda install matplotlib

- SCIPY

      conda install scipy  

- SKLEARN

      pip install sklearn

- hmmlearn

      pip install hmmlearn

- Simplejson

      conda install simplejson

- eyeD3

      pip install eyed3

- pydub

      pip install pydub

- pyAudio

      pip install pyaudio

- tkinter

      sudo apt-get install python-tk

- wave

      pip install wave


##### Notes 
it is possible to make it work on windows but I think running it on ubuntu is easier.
You might need sudo permissions (sudo pip install ...)

you might need to install:

    conda install distributed grin

if pip isn't working properly but giving an error message like 'no module named -internal', try:

    rm -rf ~/.local

## How to build

- Clone the git repository to your computer:

      git clone https://github.com/Roboy/ss18_talk_to_two.git

- open 'ss18_talk_to_two/speaker_diarization/pyAudioAnalysis'
- Clone the pyAudioAnalysis repository to  your computer
      git clone https://github.com/tyiannak/pyAudioAnalysis.git
 (yes, we want to have a folder called pyAudioAnalysis inside pyAudioAnalysis)

- return to the folder 'speaker_diarization'




## How to test
The speaker diarization is an ipython notebook that is contained in the folder pyAudioAnalysis which you just cloned from github.
Open the file 'speaker_diarization_with_visualization.ipynb' with your ipython notebook reader.
Afterwards run all the cells.

## How to use
If you want to analyze your own wav file, just
copy it to the folder input_data which is located in ss18_talk_to_two/speaker_diarization/pyAudioAnalysis.
Afterwards run speaker_diarization_with_visualization again.
Currently you can just differentiate between two speakers. That's easily changeable in the file speaker_diarization_with_visualization.ipynb if you edit the line:

result = speakerDiarization(input_path, 2)

here input_path specifies where the input file is located and 2 is the number of speakers. The program will always find as many people as you specified before.
