
Setup guide:
(For explanation of how this code works and what the classes do see our doku in confluence)

1. Setup ODAS on the matrix creator. ODAS as a new version 2.0 comming up, where it will introduce major changes that will probably break our code. Thus we have forked the current version, to make sure this will also run in the Future, so best us this repo: https://github.com/Roboy/odas

  1.1  Install ODAS on the Pi
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


  1.2 copy the config file "wip_creator.config" from this folder into odas/bin/ on the Pi.
  In this file search for the lines 255-260
  
  ```
   format = "json";
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
   and change the ip adresses to match the ones of your computer
