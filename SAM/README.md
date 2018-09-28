# SAM - Speaker and Audio Manager

ODAS is used to get the audio data and a speaker id based on direction of arrival calculations. At the same time speaker recognition is used to identify speakers based on voice features.
SAM manages both aspects and controlls the communication to both subsystems and the speech-to-text subsystem used to translate the audio input to strings.
If you want to know more about the theoretical background, check out our [best-docu-you-could-think of](https://devanthro.atlassian.net/wiki/spaces/SS18/pages/246546662/Best+Docu+you+could+think+of)



## Pre-requesites:

1. **Setup ODAS** on the matrix creator. ODAS as a new version 2.0 comming up, where it will introduce major changes that will probably break our code. Thus we have forked the current version, to make sure this will also run in the Future, so best us this repo: https://github.com/Roboy/odas
    - Install ODAS on the Pi
    ```
    sudo apt-get install libfftw3-dev
    sudo apt-get install libconfig-dev
    sudo apt-get install libasound2-dev
    ```

    ```
    git clone https://github.com/Roboy/odas

    cd odas
    mkdir build
    cd build

    cmake ../

    make
    ```
    - Copy the config file "Roboy_creator.config" from this folder into odas/bin/ on the Pi.
      In this file search for the lines 256-260

      ```
      interface: {
            type = "socket";
            ip = "192.168.178.42";
            port = 9003;
      };
      ```    
      and 323-326
      ```
      interface: {
            type = "socket";
            ip = "192.168.178.42";
            port = 9002;
      };
      ```   
      and change the ip adresses to match the one of your computer.

2. **Setup your Python Environment**. We are using **Python 2.7**. While most of our code is designed to be also compatible to Python 3, PyAudioAnalysis, a dependecy for Speaker Recognition requires 2.7. So please make sure that you have a working python 2.7 anaconda environment set up before you continue.

 If you don't have a working python 2.7 anaconda environment you can check out this page [Conda User Guide](https://conda.io/docs/user-guide/tasks/manage-python.html) or follow these steps:
  - make a new 2.7 environment in anaconda:

          conda create -n <environment_name> python=2.7 anaconda

  - activate your environment:

          source activate <environment_name>

  - verify that you are running python 2.7

          python --version

      expected printout (or a similar one):

          python 2.7.15::Anaconda custom (64-bit)

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
          
    - pyAudioAnalysis
          git clone https://github.com/tyiannak/pyAudioAnalysis.git
          pip install -e pyAudioAnalysis

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




## How to use it:
- First run **main.py** / **main.ipynb** (they both do the same thing, but appearantly on windows the matplotlib output only works in Ipython) on your computer. It's important that you run the python code first!
- When you see "Waiting for Connection..." start ODAS on the creator using the command
```
cd odas
cd bin
./odaslive -v -c Roboy_creator.cfg
```
- if you're running the **main.ipynb** you won't be getting any print outs of speaker recognition to your console. We don't know why, so just use the **main.py** file if you want to see what speaker recognition is currently doing.
