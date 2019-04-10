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
import RPi.GPIO as GPIO
import pigpio as io
import time
import pandas as pd
import os
import sys
print sys.path
import math as mt
import numpy as np
from ADS1256_definitions import * #Configuration file for the ADC settings
from pipyadc import ADS1256 #Library for interfacing with the ADC via Python
import gpiozero as gz #Library for using the GPIO with python
from dac8552.dac8552 import DAC8552, DAC_A, DAC_B, MODE_POWER_DOWN_100K #Library for using the DAC

maxRaw = 6700000
minRaw = 300000
ads = ADS1256()
ads.cal_self() 
######################## Original Code and Function Definitions from the pipyadc library ################################################
EXT1, EXT2, EXT3, EXT4 = POS_AIN0|NEG_AINCOM, POS_AIN1|NEG_AINCOM, POS_AIN2|NEG_AINCOM, POS_AIN3|NEG_AINCOM
EXT5, EXT6, EXT7, EXT8 = POS_AIN4|NEG_AINCOM, POS_AIN5|NEG_AINCOM, POS_AIN6|NEG_AINCOM, POS_AIN7|NEG_AINCOM
CH_SEQUENCE = (EXT1, EXT2)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
dac = DAC8552()
dac.v_ref = int(3.3 * dac.digit_per_v) # Start with the dac output set to vRef
act1Pos = positionConvert(aOut)
test1 = 0

def positionConvert(raw):
    '''
    This is a linearization function for converting raw digital conversions into a human readable position reading
    Position readings vary from 0 - 100%, and are based on the 4-20 mA feedback signal from the actuator
    '''
    pos = (raw - minRaw) / 50223
    return(pos)

def rawConvert(position):
    '''
    This is a linearization function for converting position readings to raw digital readings
    Position readings vary from 0 - 100%, and the raw readings vary from 0 to 8,388,608
    '''
    raw = (position * 50223) + minRaw
    return(raw)

def do_measurement():
    start = time.time()
    '''Read the input voltages from the ADC inputs. The sequence that the channels are read are defined in the configuration files
    Voltages are converted from the raw integer inputs using a voltage convert function in the pipyadc library
    The conversion to current readings is given from the datasheet for the current module by sparkfun
    '''
    raw_channels = ads.read_sequence(CH_SEQUENCE) #Read the raw integer input on the channels defined in read_sequence
    pos_channels = "{0:.1f}".format(positionConvert(raw_channels))
    print('act Position', pos_channels, time.time())
    return(pos_channels)

def modulate(modChan, m1):
    aOut = int(np.random.randint(0, high = dac.v_ref) * dac.digit_per_v) #Default arguments of none for size, and I for dtype (single value, and int for data type)
    dac.write_dac(modChan, aOut)
    act1Pos = positionConvert(aOut)
    print('DAC_A to Random', act1Pos)
    return(act1Pos)



### Setup for the modulating tests ###

modStart = time.time() #Mark the start time for the cycle
dac.write_dac(DAC_A, dac.v_ref)
print('DAC_A to HIGH')
pointTime = []
posReads = []
aOutPoints = []
wait = 0.5
while test1 < 50:
    do_measurement() # Do a single measurement of the actuator position
    pointTime = pointTime.append(time.time()) # Append the current time to a list of time points
    posReads = positionConvert.append(pos_channels[0]) # Append the position reading to a list of position readings
    aoutPoints = aOutPoints.append(act1Pos) # Append the setpoint to a list of setpoints
    if (pos_channels[0] > act1Pos) - 2 & (pos_channels[0] < act1Pos + 2):
        '''
        If the current position reading on the actuator is within 2% of the position setpoint, change the setpoint
        '''
        modulate(DAC_A)
        test1 += 1
        wait = 0.5
        time.sleep(3)
    else:
        wait = wait * 2
        time.sleep(wait)
df = pd.DataFrame({ 'time' : pointTime,
                    'Positions' : posReads,
                    'Set Point' : aOutPoints
                    })
pd.to_csv('actData.csv', sep = ',')
print('except')
GPIO.cleanup()
