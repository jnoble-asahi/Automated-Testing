#Test failed on line 127 - Arrays must be of the same length
#Check all the instances of act1pos and make sure they only have one variable




############################################
''' Quick and dirty implementation of the pi as a temperature datalogger
DAC libraries are imported but unused
######## '''
# Adding a couple of things that need to be worked out later
import os
import RPi.GPIO as GPIO
import pigpio as io
import time
import pandas as pd
import os
import sys
print(sys.path)
import math as mt
import numpy as np
from ADS1256_definitions import * #Configuration file for the ADC settings
from pipyadc import ADS1256 #Library for interfacing with the ADC via Python
import gpiozero as gz #Library for using the GPIO with python
from dac8552.dac8552 import DAC8552, DAC_A, DAC_B, MODE_POWER_DOWN_100K #Library for using the DAC
import subprocess


bash = "sudo pigpiod"
process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
maxRaw = 5625100 
minRaw = 22500
ads = ADS1256()
ads.cal_self() 
######################## Original Code and Function Definitions from the pipyadc library ################################################
EXT1, EXT2, EXT3, EXT4 = POS_AIN0|NEG_AINCOM, POS_AIN1|NEG_AINCOM, POS_AIN2|NEG_AINCOM, POS_AIN3|NEG_AINCOM
EXT5, EXT6, EXT7, EXT8 = POS_AIN4|NEG_AINCOM, POS_AIN5|NEG_AINCOM, POS_AIN6|NEG_AINCOM, POS_AIN7|NEG_AINCOM
CH_SEQUENCE = (EXT1, EXT2, EXT3)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
dac = DAC8552()
dac.v_ref = int(5 * dac.digit_per_v) # Start with the dac output set to vRef
############################### End pipyadc library#####################################################################################

def positionConvert(raw):
    '''
    This is a linearization function for converting raw digital conversions into a human readable position reading
    Position readings vary from 0 - 100%, and are based on the 4-20 mA feedback signal from the actuator
    '''
    pos = ((float(raw - minRaw)) / maxRaw)*100
    return(pos)

def rawConvert(position):
    '''
    This is a linearization function for converting position readings to raw digital readings
    Position readings vary from 0 - 100%, and the raw readings vary from 0 to 8,388,608
    '''
    raw = (position * 64000) + minRaw
    return(raw)

def currentConvert(raw):
    '''
    This is a linearization function for converting position readings to raw digital readings
    Position readings vary from 0 - 100%, and the raw readings vary from 0 to 8,388,608
    '''
    volts = float(raw * ads.v_per_digit)
    current = (volts * 186)
    return(current)

def tempConvert(raw):
    '''
    Convert temperature readings from the J type thermocouple into a readable format
    '''
    volts = float(raw * ads.v_per_digit)
    temp = (volts - 1.25) / 0.005
    return(temp)


def do_measurement():
    start = time.time()
    '''Read the input voltages from the ADC inputs. The sequence that the channels are read are defined in the configuration files
    Voltages are converted from the raw integer inputs using a voltage convert function in the pipyadc library
    The conversion to current readings is given from the datasheet for the current module by sparkfun
    '''
    raw_channels = ads.read_sequence(CH_SEQUENCE) #Read the raw integer input on the channels defined in read_sequence
    pos_channels = int(positionConvert(raw_channels[0]))
    curr = raw_channels[1]
    temp = raw_channels[2]
    #curr = int(currentConvert(raw_channels[1]))
    #temp = tempConvert(raw_channels[2])
    print('act Position', pos_channels, time.time())
    return(pos_channels, curr, temp)

def modulate(modChan):
    aOut = int(np.random.randint(0, high = dac.v_ref) * dac.digit_per_v) #Default arguments of none for size, and I for dtype (single value, and int for data type)
    dac.write_dac(modChan, aOut)
    act1Pos = int((float(aOut) / (dac.v_ref)) * 100)
    print('DAC_A to Random', act1Pos)
    return(act1Pos)

### Setup for temperature tracking ###
test1 = 0
start = time.time() #Mark the start time for the cycle
pointTime = []
tempReads = []
last = time.time()
wait = 5
i = 0
df = pd.DataFrame()
while test1 < 3600:
    if (last - start) > 1000:
        df = pd.DataFrame({ 'time' : pointTime,
                    'Temp' : posReads,
                    'Set Point' : aOutPoints
                    })
        df.to_csv('heaterTemps.csv', sep = ',')
    else:
        pass
    if (time.time() - last) > wait: 
        read = do_measurement() 
        tempTime = time.time() - start
        temp = tempConvert(read[2])
        pointTime.append(tempTime)
        tempReads.append(temp)
        i += 1
        print(temp, (tempTime), 'reading # ', i)
    
        last = time.time()
    else:
        pass
df.to_csv('heaterTemps.csv', sep = ',')
print('except')
GPIO.cleanup()


