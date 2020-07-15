# Automated-Testing
An automated test center with a web interface for electric actuators, sensors, and other control device

# Setting-up
- Format an SD card with FAT32 formatting
- Download the Raspbian Stretch OS from the raspberry pi website
- Unzip Raspbian Stretch and use Balena Etcher (or similar) to flash the OS to the formatted SD card
- Load the SD card into the pi, connect mouse, keyboard, and monitor and connect power supply
- Run through the initial set-up steps (should autoboot from the OS image on the SD card)
- Connect to a wireless network during the set-up
- Open a terminal window and run "sudo apt-get update && sudo apt-get dist-upgrade" to make sure the OS is up to date
- run 'sudo apt-get install python3-pip" to install a package manager for Python3
- run 'pip install RPi.GPIO'
- run 'pip install spidev'
- Setup the SPI bus for use:
  - run 'sudo raspi-config'
  - Select Interfacing Options -> P4 SPi -> Yes
  
# Preparing the GPIO to work with the new hardware boards
- While in a terminal window, navigate to ./boot
  - Use "cd .." then cd .." then "cd boot"
  - You can always check the available folders using "ls"
- Get the latest version of the BCM2835 libraries (required for accessing the GPIO) 
  - Run "sudo wget https://www.airspayce.com/mikem/bcm2835/bcm2835-1.58.tar.gz "
- Run "sudo tar zxvf bcm2835-1.58.tar.gz" (replace .xx. with the version number if there's been a rev)
- Run "cd bcm2835-1.58"
- Run "sudo ./configure"
- Run "make"
- Run "sudo make check"
- Run "sudo make install"

# Update packages and install python-dev
- run "sudo apt-get update"
- run "sudo apt-get install python-dev"
- 

# Clone the Github repository
The sensor and relay boards communicate with the Raspberry Pi via the SPI Bus. A couple of clever folks made open source libraries for making the SPI bus work in Python (Our language of choice for this application)
- Navigate back to the pi directory
  - From ./boot directory
    - "cd ..", then "cd home", then "cd pi"
  - Or just start a new terminal window
- Run "git clone https://github.com/pezLyfe/Automated-Testing"
- Run "cd Automated-Testing"
- Run "git clone https://github.com/pezLyfe/PiPyADC"
  - This clones the repository for working with the ADC chip and SPI bus, originally created by ul-gh on github
  - The original creators github repository is located here - https://github.com/ul-gh/PiPyADC , but we're using our own copy of the         repository for version control
    - License: GNU LGPLv2.1 
- Run "git clone https://github.com/pezLyfe/dac8552"
  - This clones the repository for working with the DAC chip and the SPI bus, originally created by adn05 on github
  - Original repository here - https://github.com/adn05/dac8552 , again we're working with our own copy for version control
    - License: GNU LGPLv2.1 
    - Copy dac8552 files into Automated-Testing directory (if using a Pi 4 Model B raspberry pi)
    
# Making the new libraries work correctly
- First install the GPIO library (if using Raspberry Pi 4 model B or newer Pi model)
  -Run "sudo apt-get update"
  -Run "sudo apt-get install rpi.gpio"
- Make sure you are in the directory ./Automated-Testing
- Check if SPI is enabled (optional):
  - Run "lsmod"
    - You should see "spi_bcm2708" or "spi_bcm2835" listed in the output. You can use the following comman to filter the list and make it easier to spot the spi entry:
      "lsmod|grep spi_"
    - SPI is now enabled
- Install Python SPI Wrapper (This activates the SPI bus):
  - Additional libraries are necessary for reading data from the SPI bus in Python. To check if these libraries are installed: 
    - Run “sudo apt-get install -y python-dev python3-dev”
    - Run “sudo apt-get install -y python-spidev python3-spidev”
- Download ‘py-spidev’ and compile it ready for use. From Automated-Testing directory:
  - Run “git clone https://github.com/Gadgetoid/py-spidev.git”
  - Run “cd py-spidev”
  - Run “sudo python setup.py install”
  - Run “sudo python3 setup.py install”
  - Run “cd ..”
- Now install the pigpio library
  - In directory ./Automated-Testing
    - run "wget abyz.me.uk/rpi/pigpio/pigpio.tar"
    - run "tar xf pigpio.tar
    - run "cd PIGPIO"
    - run "make"
    - run "sudo make install"
- To install the Python client library for Cloud Datastore:
  - Install the client library locally by using pip:
    - Run “pip install google-cloud-datastore”

# Assemble the Pi with the external hardware and enclosure
-Change jumpers:
    - move 3v3 to VCC jumper and put across 5v and VCC
    - take off AD0 to ADJ and AD1 to LDR jumpers

# Set the zero off-set and span of the current - voltage converters

# Connect one or two modulating actuators and run Ttest.py



