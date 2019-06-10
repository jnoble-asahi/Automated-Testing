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
import sys
from ADS1256_definitions import * #Configuration file for the ADC settings
from pipyadc import ADS1256 #Library for interfacing with the ADC via Python
from dac8552.dac8552 import DAC8552, DAC_A, DAC_B, MODE_POWER_DOWN_100K #Library for using the DAC
#from sklearn.linear_model import LinearRegression

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
        + ", ".join(["{: 8d}".format(i) for i in digits])
        +

"""

The position value being sent is:
Channel 
"""
        + ", ".join(["{: 8.3f}".format(i) for i in positions])
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
    raw_channels = ads.read_sequence(channel) #Read the raw integer input on the channels defined in read_sequence
    #pos_channels = int(positionConvert(raw_channels[0]))
    nice_output(raw_channels, positions)
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
chanDict = {1 : 'EXT1', 2 : 'EXT2'}
aOutDict = {1 : 'DAC_A', 2 : 'DAC_B'}
validChans = list(chanDict.keys())

channel = input('Please enter the channel # ')

if channel not in validChans:
    raise ValueError('Channel can only be 1 or 2')
else:
    print('Setting IO addresses')

# Set the actuator to full close
pos = 0
move(pos, channel)

while True:
    i = prompt()
    if i != 'Y':
        do_measurement(channel, pos)
    elif i == 'Y':
        False
    else:
        break

pos = 100
move(pos, channel)
'''
This shit didn't work, find another way to pause until instructions are given to move on
Also, this shit needs to display the current status of the IV converter, look that up from the example code
'''
while True:
    i = prompt()
    if i != 'Y':
        do_measurement(channel, pos)
    elif i == 'Y':
        False
    else:
        break

### Setup for the modulating tests ###
positions = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
readings = []
start = time.time()
i = 0
for i in range(len(positions)):
    if time.time() - start < 10: # Give the actuator time to move into position
        pass
    else:
        pos = []
        for j in range(15):
            pos[j] = do_measurement(channel, positions[i])
            time.sleep(1)
    readings[i] = np.mean(pos)
    move(positions[i], channel)
    start = time.time()

df = pd.DataFrame()
df['readings'] = readings
df['positions'] = positions
df.to_csv('calibrationReadings.csv', sep = ',')


'''
x = df['readings']
y = df['positions']
regression_model = LinearRegression()
regression_model.fit(x,y)

for idx, col_name in enumerate(x.columns):
    print("Coefficient for {} is {}".format(col_name, regression_model.coef_[0][idx]))
'''
