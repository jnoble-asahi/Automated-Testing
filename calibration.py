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
import subprocess
import time
import pandas as pd
import numpy as np
import sys
from ADS1256_definitions import * #Configuration file for the ADC settings
from pipyadc import ADS1256 #Library for interfacing with the ADC via Python
from dac8552.dac8552 import DAC8552, DAC_A, DAC_B, MODE_POWER_DOWN_100K #Library for using the DAC
#from sklearn.linear_model import LinearRegression


# Start the pigpio daemon 
bash = "sudo pigpiod" 
process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

maxRaw = []
minRaw = []
ads = ADS1256()
ads.cal_self() 
dac = DAC8552()
dac.v_ref = 5

def nice_output(digits, positions):
    sys.stdout.write(
          "\0337" # Store cursor position
        +
"""

The position value being read is:
Channel
"""
        + ", ".join(["{: 8d}".format(digits)])
        +

"""

The position value being sent is:
Channel 
"""
        + ", ".join(["{: 8.3f}".format(positions)])
        + "\n\033[J\0338" # Restore cursor position etc.
    )

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

def do_measurement(channel, position):
    '''Read the input voltages from the ADC inputs. The sequence that the channels are read are defined in the configuration files
    Voltages are converted from the raw integer inputs using a voltage convert function in the pipyadc library
    The conversion to current readings is given from the datasheet for the current module by sparkfun
    '''
    raw_channels = ads.read_oneshot(channel) #Read the raw integer input on the channels defined in read_sequence
    #pos_channels = int(positionConvert(raw_channels[0]))
    nice_output(raw_channels, position)
    return(raw_channels)

def move(position, chan):
    aOut = int((float(position)/100) * (dac.v_ref * dac.digit_per_v))
    dac.write_dac(chan, aOut)
    print(aOut)

def prompt():
    x = input("Ready to continue? (Y or N)")
    return(x)

EXT1, EXT2, EXT3, EXT4 = POS_AIN0|NEG_AINCOM, POS_AIN1|NEG_AINCOM, POS_AIN2|NEG_AINCOM, POS_AIN3|NEG_AINCOM
EXT5, EXT6, EXT7, EXT8 = POS_AIN4|NEG_AINCOM, POS_AIN5|NEG_AINCOM, POS_AIN6|NEG_AINCOM, POS_AIN7|NEG_AINCOM

# A dictionary that maps the channel number input from the user to the addresses in pipyadc
chanDict = {1 : EXT1, 2 : EXT2}
aOutDict = {1 : DAC_A, 2 : DAC_B}
validChans = list(chanDict.keys())

channel = input('Please enter the channel # ')
chan = chanDict[channel]
out = aOutDict[channel]

if channel not in validChans:
    raise ValueError('Channel can only be 1 or 2')
else:
    print('Setting IO addresses')

# Set the actuator to full close
pos = 0
move(pos, out)

try: 
    while True:
        do_measurement(chan, pos)
except KeyboardInterrupt:
    pos = 100
    move(pos, out)
    #i = str(prompt())
    #if i == 'Y':
    #    break
    #else:
    #    continue




try:
    while True:
        do_measurement(chan, pos)
    #i = prompt()
    #if i == 'Y':
    #    break
    #else:
except KeyboardInterrupt:
    pos = 0
    move(pos, out)       

'''
Using keyboard interrupt, the try/except exits past the next for loop. I gave the except block something to do, check if it exits correctly now
'''

### Setup for the modulating tests ###
places = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
readings = []
start = time.time()
i = 0
x = 0
# The top level loop executes several times while waiting for the comparision operation to return True
# Re-organize the loop, or break it into functions such that the top level loop won't increment until the actuator has moved, and
# the readings have finished being taken
for i in range(len(places)):
    p = places[i]
    for j in range(20):
        pos = []
        move(p, out)
        if (j > 10):
            pos.append(do_measurement(chan,p))
            time.sleep(1)
        else:
            time.sleep(1)
        x = np.mean(pos)
        readings.append(x)
    
df = pd.DataFrame()
df['readings'] = readings
df['positions'] = places
df.to_csv('calibrationReadings.csv', sep = ',')


'''
x = df['readings']
y = df['positions']
regression_model = LinearRegression()
regression_model.fit(x,y)

for idx, col_name in enumerate(x.columns):
    print("Coefficient for {} is {}".format(col_name, regression_model.coef_[0][idx]))
'''
