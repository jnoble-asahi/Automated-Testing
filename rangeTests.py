############################################
''' This is a rough draft of code required to run the actuation tester prototype
The script loads two other programs - ADC_Script and DAC_Script
The project requires a large number of dependencies from other libraries
Full details on dependencies and set-up instructions on Github here: exampleURL.com
Pin callouts in this program refer to the wiringPI addresses and not GPIO pin numbers
This script written by Chris May - pezLyfe on github
######## '''
import os
import RPi.GPIO as GPIO
import pigpio as io
import time
import os
import sys
print sys.path
import math as mt
import numpy as np
from ADS1256_definitions import * #Configuration file for the ADC settings
from pipyadc import ADS1256 #Library for interfacing with the ADC via Python
import gpiozero as gz #Library for using the GPIO with python
from dac8552.dac8552 import DAC8552, DAC_A, DAC_B, MODE_POWER_DOWN_100K #Library for using the DAC

######################## Original Code and Function Definitions from the pipyadc library ################################################
EXT1, EXT2, EXT3, EXT4 = POS_AIN0|NEG_AINCOM, POS_AIN1|NEG_AINCOM, POS_AIN2|NEG_AINCOM, POS_AIN3|NEG_AINCOM
EXT5, EXT6, EXT7, EXT8 = POS_AIN4|NEG_AINCOM, POS_AIN5|NEG_AINCOM, POS_AIN6|NEG_AINCOM, POS_AIN7|NEG_AINCOM

# Specify here an arbitrary length list (tuple) of arbitrary input channel pair
# eight-bit code values to scan sequentially from index 0 to last.
# Eight channels fit on the screen nicely for this example..
CH_SEQUENCE = (EXT1, EXT2, EXT3, EXT4, EXT5, EXT6, EXT7)
################################################################################
    ### STEP 1: Initialise ADC object using default configuration:
    # (Note1: See ADS1256_default_config.py, see ADS1256 datasheet)
    # (Note2: Input buffer on means limited voltage range 0V...3V for 5V supply)
ads = ADS1256()
### STEP 2: Gain and offset self-calibration:
ads.cal_self() 

def do_measurement():
    start = time.time()
    '''Read the input voltages from the ADC inputs. The sequence that the channels are read are defined in the configuration files
    Voltages are converted from the raw integer inputs using a voltage convert function in the pipyadc library
    The conversion to current readings is given from the datasheet for the current module by sparkfun
    '''
    while (time.time() - start) < 6000:
        raw_channels = ads.read_sequence(CH_SEQUENCE) #Read
        #voltages = [i * ads.v_per_digit for i in raw_channels] #Convert the raw input to a voltage reading using the pipyadc library function
        #current = [(i - 2.5)/0.066 for i in voltages] #Convert the voltage reading to a current value for the current sensor
        nice_output(raw_channels, raw_channels)

#############################################################################
# Format nice looking text output:
def nice_output(digits, current):
    sys.stdout.write(
          "\0337" # Store cursor position
        +
"""
These are the sample values converted to voltage in V for the channels:
AIN0,  AIN1, AIN2, AIN3, AIN4, AIN5, AIN6, AIN7 
"""
        + ", ".join(["{: 8.3f}".format(i) for i in raw_channels])
        + "\n\033[J\0338" # Restore cursor position etc.
    )

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

test1 = 0
### Setup for the modulating tests ###
dac = DAC8552()
modStart = time.time() #Mark the start time for the cycle
dac.v_ref = int(3.3 * dac.digit_per_v) # Start with the dac output set to vRef
aOut = dac.v_ref
dac.write_dac(DAC_A, aOut)
print('DAC_A to HIGH')
while test1 < 1000:
    if time.time() - modStart > 20:
        aOut = 0
        dac.write_dac(DAC_A, aOut)
    do_measurement()
print('except')
GPIO.cleanup()
