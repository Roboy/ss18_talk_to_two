# Talk to two

This will be the most important stuff regarding this impressive project. It's about beeing able to talk to two people at the same time. And these are the Instructions to make it work.

The goal of this project is to have a conversation with three people including roboy. We want him to be able to tell who is saying what and store this information, so a real conversation is possible.

Additionally we created a breakout board with new better microphones and are currently working on the signal handling and software for it.

For more detailed and theoretic information about the project please check out our [best docu you could think of](https://devanthro.atlassian.net/wiki/spaces/SS18/pages/246546662/Best+Docu+you+could+think+of).

## Transformatrix

In this subproject we're developing our own microphone array. You can/will find these software parts in our repository:

  -  Verilog driver for the SIMIC (solved)
  -  Communication module for ARM-Core and FPGA (solved)
  -  Python driver to access the audio data as Numpy array (far far away)
  - the Lowpass filter and decimation implementation and algorithm in Matlab (solved)
  - the Lowpass filter ported onto the FPGA (still in progress)

Please find more information and the code in the folder called `transformatrix`. There's an additional README where you can find more detailed information about its functionality and how to use it.

##### Microphone holder

We designed our costum microphone holder and 3D printed it. In the folder `stuff_related_to_custom_mic_array`you can find all the files we used to print it.


## SAM
SAM - Speaker and Audio Manager. Handles the identification of who is speaking using direction of arrival information and speaker recognition. More information can be found in the README in the the folder `SAM`.


## Speaker diarization

In order to be able to have a conversation with multiple people the question 'who is talking when?' raises. Our first approach to solve this question was speaker diarization.

Please find more information and the code in the folder called `speaker_diarization`. There's an additional README where you can find more detailed information about its functionality and how to use it.

## Multiparty Dialog

The current dialog system was adapted in order to be able to not only understand that there are different people talking but to have a real meaningful conversation with more than one person. This part was directly modified in the [Dialog System](https://github.com/Roboy/roboy_dialog/tree/negin_multi_party_dialog_3)

## odas_initial_experiments

Here you can find some of our initial experiments with ODAS to understand how it works and how we can use it.
