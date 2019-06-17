'''
Make a class constructor that stores all parameters for each test that's running

Push all of the test code into a canned function that gets called once per loop
'''


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
print(sys.path)
import math as mt
import numpy as np
from ADS1256_definitions import * #Configuration file for the ADC settings
from pipyadc import ADS1256 #Library for interfacing with the ADC via Python
import adc_dac_config as an
import dac8552.dac8552 as dac1
from dac8552.dac8552 import DAC8552, DAC_A, DAC_B, MODE_POWER_DOWN_100K #Library for using the DAC
import subprocess

maxRaw = 5625100 
minRaw = 22500


ads = ADS1256()
dac = DAC8552()
ads.cal_self()

DAC_A = dac1.DAC_A
DAC_B = dac1.DAC_B

CH1_SEQUENCE = (an.INPUTS_ADDRESS[0], an.INPUTS_ADDRESS[2], an.INPUTS_ADDRESS[5] ) #Position, Current, Temperature channels
CH2_SEQUENCE =  (an.INPUTS_ADDRESS[1], an.INPUTS_ADDRESS[3], an.INPUTS_ADDRESS[6] ) #Position, Current, Temperature channels

### Setup for the modulating tests ###
stamp1 = time.time()
stamp2 = time.time() # Used as a reference for the datalogger
apR1 = apR2 = dac.v_ref * dac.digit_per_v # The raw value for a high output on the DAC channels
apC1 = 100
apC2 = 100 # Convert the raw value to a position readingg
pos1 =[]
pos2 = [] # Create empty lists to add position readings to
cur1 = []
cur2 = [] # Create empty lists to add current readings to
temp1 = []
temp2 = [] # Create empty lists to add temperature readings to
wt1 = time.time()
wt2 = time.time() # Create a timestamp to compare cycle times
ct1 = []
ct2 = [] # Create empty lists to store cycle times
a1 = [] 
a2 = [] # Create empty lists to add test setpoints to
t1 = 0
t2 = 0 # Variable to track cycle counts
w1 = 1.5

w2 = 1.5 # initialize a wait time to reach the next setpoint
slack1 = 2
slack2 = 2

dac.write_dac(DAC_A, apR1) # Set DAC0 to full open
print('DAC_A to HIGH')

dac.write_dac(DAC_B, apR2) # Set DAC1 to full open
print('DAC_B to HIGH')
t1State = t2State = True

'''
There needs to be two variables to track current time. One should have the current value of wX (wait time for each test), and one should be
a list of wait times for each cycle.

Program flow should go: Check the delta between the current time and the wait time. If it's more than the wait time, do stuff. If it's 
less than the wait time, wait some more.

If it's more than the wait time and the actuator position is within the required range, then update the variable and append the cycle time
to the list
'''

while True: # If either t1 or t2 still have cycles left, continue the test
    if (t1 < 1000000) & ((time.time() - wt1) > w1):
        pos1Read = int(an.positionConvert(an.single_measurement(CH1_SEQUENCE[0]),1))
        cur1Read = an.single_measurement(CH1_SEQUENCE[1])
        temp1Read = an.single_measurement(CH1_SEQUENCE[2]) 
        #an.do_measurement(CH1_SEQUENCE, 0) # Measure a sequence of inputs outline in CH1_Sequence
        pos1.append(pos1Read)
        cur1.append(cur1Read)
        temp1.append(temp1Read)
        ct1.append(time.time())
        a1.append(apC1)
        lastTime1 = time.time() - stamp1
        if lastTime1 > 3600:
            df1 = pd.DataFrame({ 'time' : ct1,
                        'Positions' : pos1,
                        'Current' : cur1,
                        'Temperature' : temp1,
                        'Set Point' : a1
                            })
            df1.to_csv('act1Data.csv', sep = ',')
            stamp1 = time.time()
        else:
            pass
        if pos1Read in range(int(apC1 - slack1), int(apC1 + slack1)):
            '''
            If the current position reading on the actuator is within 2% of the position setpoint, change the setpoint
            '''
            time.sleep(1)
            apC1 = an.modulate(DAC_A)
            ct1.append(time.time() - wt1)
            wt1 = time.time()
            print('Act 1 Cycle Number is ', t1, 'Actuator Current Draw', cur1Read, 'Actuator Temperature ', temp1Read)
            t1 += 1
            w1 = 1.5
            slack1 = 2
        else:
            w1 = w1 * 1.5
            slack1 = slack1*1.10
            print('wait time: ', w1, 'Act1 Set Point', int(apC1 - slack1), pos1Read, int(apC1 + slack1), 'Current Draw ', cur1Read, 'Actuator Temperature ', temp1Read)
            time.sleep(0.5)
    else:
        t1State = False
    if (t2 < 1000000) & ((time.time() - wt2) > w2):
        #read = an.do_measurement(CH2_SEQUENCE, 1) # Measure a sequence of inputs outline in CH1_Sequence
        pos2Read = int(an.positionConvert(an.single_measurement(CH2_SEQUENCE[0]), 2))
        cur2Read = an.single_measurement(CH2_SEQUENCE[1])
        temp2Read = an.single_measurement(CH2_SEQUENCE[2]) 
        #an.do_measurement(CH1_SEQUENCE, 0) # Measure a sequence of inputs outline in CH1_Sequence
        pos2.append(pos2Read)
        cur2.append(cur2Read)
        temp2.append(temp2Read)
        ct2.append(time.time())
        a2.append(apC2)
        lastTime2 = time.time() - stamp2
        if lastTime2 > 3600:
            df2 = pd.DataFrame({ 'time' : ct2,
                        'Positions' : pos2,
                        'Current' : cur2,
                        'Temperature' : temp2,
                        'Set Point' : a2
                        })
            df2.to_csv('act2Data.csv', sep = ',')
            stamp2 = time.time()
        else:
            pass
        if pos2Read in range(int(apC2 - slack2), int(apC2 + slack2)):
            '''
            If the current position reading on the actuator is within 2% of the position setpoint, change the setpoint
            '''
            time.sleep(1)
            apC2 = an.modulate(DAC_B)
            ct2.append(time.time() - wt2)
            wt2 = time.time()
            print('Act2 Cycle Number is ', t2, 'Actuator Current Draw', cur2Read, 'Actuator Temperature ', temp2Read)
            t2 += 1
            w2 = 1.5
            slack2 = 2
        else:
            w2 = w2 * 1.5
            slack2 = slack2*1.10
            print('wait time is: ', w2, 'Act2 Set Point', int(apC2 - slack2), pos2Read, int(apC2 + slack2), 'Current Draw ', cur2Read, 'Actuator Temperature ', temp2Read)
            time.sleep(0.5)
    else:
        t2State = False
df1 = pd.DataFrame({ 'time' : ct1,
                    'Positions' : pos1,
                    'Current' : cur1,
                    'Temperature' : temp1,
                    'Set Point' : a1})

df1.to_csv('act2Data.csv', sep = ',')

df2 = pd.DataFrame({ 'time' : ct2,
                    'Positions' : pos2,
                    'Current' : cur2,
                    'Temperature' : temp2,
                    'Set Point' : a2})

df2.to_csv('act2Data.csv', sep = ',')

print('sacrificing IO daemons')

bash = "sudo killall pigpiod" 
process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

print('except')

