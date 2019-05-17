############################################
''' This is a rough draft of code required to run the actuation tester prototype
The script loads two other programs - ADC_Script and DAC_Script
The project requires a large number of dependencies from other libraries
Full details on dependencies and set-up instructions on Github here: exampleURL.com
Pin callouts in this program refer to the wiringPI addresses and not GPIO pin numbers
This script written by Chris May - pezLyfe on github
######## '''
# Adding a couple of things that need to be worked out later
import os
import pigpio as io
import time
import pandas as pd
import numpy as np
from ADS1256_definitions import * #Configuration file for the ADC settings
from pipyadc import ADS1256 #Library for interfacing with the ADC via Python
from dac8552.dac8552 import DAC8552, DAC_A, DAC_B, MODE_POWER_DOWN_100K #Library for using the DAC

maxRaw = [6700000, 6700000 ]
minRaw = [22500, 22500 ]
ads = ADS1256()
ads.cal_self() 
######################## Original Code and Function Definitions from the pipyadc library ################################################
EXT1, EXT2, EXT3, EXT4 = POS_AIN0|NEG_AINCOM, POS_AIN1|NEG_AINCOM, POS_AIN2|NEG_AINCOM, POS_AIN3|NEG_AINCOM
EXT5, EXT6, EXT7, EXT8 = POS_AIN4|NEG_AINCOM, POS_AIN5|NEG_AINCOM, POS_AIN6|NEG_AINCOM, POS_AIN7|NEG_AINCOM
CH_SEQUENCE = (EXT1, EXT2)
dac = DAC8552()
dac.v_ref = 5


def positionConvert(raw):
    '''
    This is a linearization function for converting raw digital conversions into a human readable position reading
    Position readings vary from 0 - 100%, and are based on the 4-20 mA feedback signal from the actuator
    '''
    pos = (float(raw - minRaw)) / 65535
    return(pos)

def rawConvert(position):
    '''
    This is a linearization function for converting position readings to raw digital readings
    Position readings vary from 0 - 100%, and the raw readings vary from 0 to 8,388,608
    '''
    raw = (position * 65535) + minRaw
    return(raw)

def do_measurement():
    start = time.time()
    '''Read the input voltages from the ADC inputs. The sequence that the channels are read are defined in the configuration files
    Voltages are converted from the raw integer inputs using a voltage convert function in the pipyadc library
    The conversion to current readings is given from the datasheet for the current module by sparkfun
    '''
    raw_channels = ads.read_sequence(CH_SEQUENCE) #Read the raw integer input on the channels defined in read_sequence
    #pos_channels = int(positionConvert(raw_channels[0]))
    print('act Position', raw_channels[0])
    print('act2 Position', raw_channels[1])
    return(raw_channels)

def modulate(position):
    aOut = int((float(position)/100) * (dac.v_ref * dac.digit_per_v))
    dac.write_dac(DAC_A, aOut)
    dac.write_dac(DAC_B, aOut)
    print(aOut)

### Setup for the modulating tests ###
positions = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
start = time.time()
i = 0
while i < len(positions):
    if time.time() - start < 30:
        do_measurement()
        time.sleep(1)
    else:
        print('moving to ', positions[i])
        modulate(positions[i])
        start = time.time()
        i += 1
print('except')
GPIO.cleanup()

