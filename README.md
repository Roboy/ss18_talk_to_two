# Talk to two

This will be the most important stuff regarding this impressive project. It's about beeing able to talk to two people at the same time. And these are the Instructions to make it work.

The goal of this project is to have a conversation with three people including roboy. We want him to be able to tell who is saying what and store this information, so a real conversation is possible.

Additionally we created a breakout board with new better microphones and are currently working on the signal handling and software for it.

For more detailed and theoretic information about the project please check out our [best docu you could think of](https://devanthro.atlassian.net/wiki/spaces/SS18/pages/246546662/Best+Docu+you+could+think+of).

## Transformatrix

In this subproject we're developing our own microphone array. You can/will find these software parts in our repository:

  -  Verilog driver for the SIMIC (in progress)
  -  Communication module for ARM-Core and FPGA (not implemented yet)
  -  Python driver to access the audio data as Numpy array (far far away)

For now everything is running on a Mojo V3. You'll obviously need one if you want to use the code from this repository.

Please find more information and the code in the folder called `transformatrix`. There's an additional README where you can find more detailed information about its functionality and how to use it.

## SAM
SAM - Speaker and Audio Manager. Handles identifing who is speaking. More info in the Readme in the the folder SAM.

## Breakout board

We designed our costum breakout board and 3D printed it. In the folder `stuff_related_to_custom_mic_array`you can find all the files we used to print it.

## Speaker diarization

In order to be able to have a conversation with multiple people the question 'who is talking when?' raises. Our first approach to solve this question was speaker diarization.

Please find more information and the code in the folder called `speaker_diarization`. There's an additional README where you can find more detailed information about its functionality and how to use it.
