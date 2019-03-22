# Automated-Testing
An automated test center with a web interface for electric actuators, sensors, and other control devices

# Setting-up
- Format an SD card with FAT32 formatting
- Download the Raspbian Stretch OS from the raspberry pi website
- Unzip Raspbian Stretch and use Balena Etcher (or similar) to flash the OS to the formatted SD card
- Load the SD card into the pi, connect mouse, keyboard, and monitor and connect power supply
- Run through the initial set-up steps (should autoboot from the OS image on the SD card)
- Connect to a wireless network during the set-up
- Open a terminal window and run "sudo apt-get update && sudo apt-get dist-upgrade" to make sure the OS is up to date
- run 'sudo apt-get install python3-pip" to install a package manager for Python3
- Use pip to get the following libraries and dependancies for Python3:
  - update me
  - and some more things
  
# Preparing the GPIO to work with Sensors and Relays
- Get the latest version of the BCM2835 libraries (required for accessing the GPIO?) 
  - Currently at http://www.airspayce.com/mikem/bcm2835/bcm2835-1.58.tar.gz 
- Run "tar zxvf bcm2835-1.xx.tar.gz" (replace .xx. with the version number)
- Run "cd bcm2835-1.xx"
- Run "./configure"
- Run "make"
- Run "sudo make check"
- Run "sudo make install"

# Sharing libraries and other things to make Python work with the Waveshare hardware
The Waveshare ADC/DAC board we're working with uses I2C to communicate with hte Pi. I2C doesn't seem to be fully supported yet with Python, so we'll use the test files that came with the board. The test files are written in C, so we'll need to make some shared libraries so the two languages function together.
- Navigate to bcm2835-1.58/src and run "gcc -shared -o libbcm2835.so -fPIC bcm2835.c"
- Copy the libbcm2835.so file into /usr/local/lib (use sudo mv <filename> <destination>
- Clone the python bindings for libbcm2835 from https://github.com/mubeta06/py-libbcm2835 into the /usr/local/lib
- Go to the root of the download and run "sudo python3 setup.py install"

# Installing the 
  
  
- Set the current directory to where you want your program files
- Run "git clone <url> to clone the repository into the current directory
- Run "git branch -b <url> to make a new branch

