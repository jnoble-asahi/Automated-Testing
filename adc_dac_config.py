'''
Notes on the differences in GPIO pin numbering schemes:
- For a variety of reasons, there's different pin numbering schemes across the GPIO physical header position (the 40 pin connector on the pi)
the pin numbering on the BCM2835 chip, the pin numbering scheme used by the wiringPI module, and the scheme used for the piGPIO module
- The pypiADC module used in this program uses *phys() method to initialize wiringPi. In this case, pin numbers called by wiringPI refer to the
physical location on the GPIO header
- The pigpio module uses the BCM pin numbering scheme, layout here: https://abyz.me.uk/rpi/pigpio/#Type_3
- Compatibility issues may come up in the future as hardware architectures change 
    - The creator of wiringPI made their schema to future proof against changes
- Refer to the layout in the documentation to find the pin numbers under each scheme
- A list of resources for pin numbering here:
    - https://abyz.me.uk/rpi/pigpio/#Type_3
        - pigpio pin numbering schema (based on BCM pinout)
    - http://wiringpi.com/pins/
        - Pin layouts for wiringPI
    - http://wiringpi.com/reference/setup/
        - Overview of the different setup methods available for wiringPI
'''
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
import os
import sys
import math as mt
import numpy as np
from ADS1256_definitions import * #Configuration file for the ADC settings
from pipyadc import ADS1256 #Library for interfacing with the ADC via Python
import gpiozero as gz #Library for using the GPIO with python
from dac8552.dac8552 import DAC8552, DAC_A, DAC_B, MODE_POWER_DOWN_100K #Library for using the DAC
import subprocess

# Start the pigpio daemon 
print('summoning IO daemons')
# Start the pigpio daemon 
bash = "sudo pigpiod" 
process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

maxRaw = [5625100, 5625100] 
minRaw = [22500, 22500]

ads = ADS1256()
ads.cal_self() 
######################## Original Code and Function Definitions from the pipyadc library ################################################
EXT1, EXT2, EXT3, EXT4 = POS_AIN0|NEG_AINCOM, POS_AIN1|NEG_AINCOM, POS_AIN2|NEG_AINCOM, POS_AIN3|NEG_AINCOM
EXT5, EXT6, EXT7, EXT8 = POS_AIN4|NEG_AINCOM, POS_AIN5|NEG_AINCOM, POS_AIN6|NEG_AINCOM, POS_AIN7|NEG_AINCOM
INPUTS_ADDRESS = (EXT1, EXT2, EXT3, EXT4, EXT5, EXT6, EXT7, EXT8)
dac = DAC8552()
dac.v_ref = int(5 * dac.digit_per_v) # Start with the dac output set to vRef


def positionMeasurement(chanIn):
    '''
    Read an ADC input and linearize the raw input to a position value of 0 - 100%
    '''
    x = ads.read_oneshot(chanIn) #Read the raw integer input on the channels
    y = ((float(x - minRaw)) / maxRaw)*100
    return(y)

def positionConvert(pos, chan):
    '''Take the raw value from a position measurment and convert that to a value of 0 - 100%
    '''
    x = ((float(float(pos - minRaw[chan]) / maxRaw[chan])) * 100)
    return(x)

def rawConvert(y):
    '''
    Linearization function for converting position readings to raw digital readings
    Position readings vary from 0 - 100%, and the raw readings vary from 0 to 8,388,608
    '''
    x = (y * 64000) + minRaw
    return(x)

def currentMeasurement(chanIn):
    '''
    Read and linearize a current input to Amps
    '''
    x = ads.read_oneshot(chanIn) #Read the raw integer input on the channels
    y = float(x * ads.v_per_digit)
    current = (2.5 - y) * 186
    return(current)

def currentConvert(curr):
    '''Linearize a raw current input reading
    '''
    x = (2.5 - float(curr * ads.v_per_digit))*186
    return(x)

def tempMeasurement(chanIn):
    '''
    Convert temperature readings from the J type thermocouple into a readable format
    '''
    x = ads.read_oneshot(chanIn) #Read the raw integer input on the channels
    y = float(x * ads.v_per_digit)
    temp = (y - 1.25) / 0.005
    return(temp)

def tempConvert(temp):
    '''Convert a temperature reading from the J type thermocouple in a fahrenheit reading
    '''
    x = float(temp * ads.v_per_digit - 1.25)/ 0.005
    return(x)

def single_measurement(chanIn):
    '''Read the input voltages from the ADC inputs, returns as a raw integer value
    '''
    raw_channels = ads.read_oneshot(chanIn) #Read the raw integer input on the channels
    return(raw_channels)

def modulate(modChan):
    aOut = int(np.random.randint(0, high = dac.v_ref) * dac.digit_per_v) #Default arguments of none for size, and I for dtype (single value, and int for data type)
    dac.write_dac(modChan, aOut)
    aPos = int((float(aOut) / (dac.v_ref * dac.digit_per_v)) * 100)
    print( modChan, ' to Random', aPos)
    return(aPos)

def do_measurement(inputs, chan):
    '''Read the input voltages from the ADC inputs. The sequence that the channels are read are defined in the configuration files
    Voltages are converted from the raw integer inputs using a voltage convert function in the pipyadc library
    The conversion to current readings is given from the datasheet for the current module by sparkfun
    '''
    raw_channels = ads.read_sequence(inputs) #Read the raw integer input on the channels defined in read_sequence
    pos_channel = int(positionConvert(raw_channels[0], chan))
    curr = int(currentConvert(raw_channels[1]))
    temp = tempConvert(raw_channels[2])
    return(pos_channel, curr, temp, time.time())