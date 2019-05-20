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
stamp1 = stamp2 = time1 = time2 = time.time() # Used as a reference for the datalogger
apR1 = apR2 = dac.v_ref * dac.digit_per_v # The raw value for a high output on the DAC channels
apC1 = 100
apC2 = 100 # Convert the raw value to a position readingg
pos1 = pos2 = [] # Create empty lists to add position readings to
cur1 = cur2 = [] # Create empty lists to add current readings to
temp1 = temp2 = [] # Create empty lists to add temperature readings to
ct1 = ct2 = [] # Create empty lists to add timestamps to
a1 = a2 = [] # Create empty lists to add test setpoints to
t1 = t2 = 0 # Create empty lists to add cycle counts to
w1 = w2 = 1.5 # initialize a wait time to reach the next setpoint
slack1 = slack2 = 2

dac.write_dac(DAC_A, apR1) # Set DAC0 to full open
print('DAC_A to HIGH')

dac.write_dac(DAC_B, apR2) # Set DAC1 to full open
print('DAC_B to HIGH')
t1State = t2State = True

while True: # If either t1 or t2 still have cycles left, continue the test
    if (t1 < 1000000) & ((time.time() - stamp1) > w1):
        read = an.do_measurement(CH1_SEQUENCE, 0) # Measure a sequence of inputs outline in CH1_Sequence
        pos1.append(read[0])
        cur1.append(read[1])
        temp1.append(read[2])
        ct1.append(time.time())
        a1.append(apC1)
        lastTime1 = time.time() - stamp1
        if lastTime1 > 3600:
            df1 = pd.DataFrame({ 'time' : time.time(),
                        'Positions' : pos1,
                        'Current' : cur1,
                        'Temperature' : temp1,
                        'Set Point' : a1})
            df1.to_csv('act1Data.csv', sep = ',')
            stamp1 = time.time()
        else:
            pass
        if read[0] in range(int(apC1 - slack1), int(apC1 + slack1)):
            '''
            If the current position reading on the actuator is within 2% of the position setpoint, change the setpoint
            '''
            time.sleep(1)
            apC1 = an.modulate(DAC_A)
            print('Act 1 Cycle Number is ', t1, 'Actuator Current Draw', read[1], 'Actuator Temperature ', read[2] )
            t1 += 1
            w1 = 1.5
            slack1 = 2
        else:
            w1 = w1 * 1.5
            slack1 = slack1*1.25
            print('Act1 Set Point', int(apC1 - slack1), read[0], int(apC1 + slack1), 'Current Draw ', read[1], 'Actuator Temperature ', read[2])
            time.sleep(0.5)
    else:
        t1State = False
    if (t2 < 1000000) & ((time.time() - stamp2) > w2):
        read = an.do_measurement(CH2_SEQUENCE, 1) # Measure a sequence of inputs outline in CH1_Sequence
        pos2.append(read[0])
        cur2.append(read[1])
        temp2.append(read[2])
        ct2.append(time.time())
        a2.append(apC2)
        lastTime2 = time.time() - stamp2
        if lastTime2 > 3600:
            df2 = pd.DataFrame({ 'time' : time.time(),
                        'Positions' : pos2,
                        'Current' : cur2,
                        'Temperature' : temp2,
                        'Set Point' : a2})
            df2.to_csv('act2Data.csv', sep = ',')
            stamp2 = time.time()
        else:
            pass
        if read[0] in range(int(apC2 - slack2), int(apC2 + slack2)):
            '''
            If the current position reading on the actuator is within 2% of the position setpoint, change the setpoint
            '''
            time.sleep(1)
            apC2 = an.modulate(DAC_B)
            print('Act2 Cycle Number is ', t2, 'Actuator Current Draw', read[1], 'Actuator Temperature ', read[2])
            t2 += 1
            w2 = 1.5
            slack2 = 2
        else:
            w2 = w2 * 1.5
            slack2 = slack2*1.25
            print('Act2 Set Point', int(apC2 - slack2), read[0], int(apC2 + slack2), 'Current Draw ', read[1], 'Actuator Temperature ', read[2] )
            time.sleep(0.5)
    else:
        t2State = False
df1 = pd.DataFrame({ 'time' : time.time(),
                    'Positions' : pos1,
                    'Current' : cur1,
                    'Temperature' : temp1,
                    'Set Point' : a1})

df1.to_csv('act2Data.csv', sep = ',')

df2 = pd.DataFrame({ 'time' : time.time(),
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

