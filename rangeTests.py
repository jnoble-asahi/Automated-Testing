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

ads = ADS1256()
dac = DAC8552()
ads.cal_self()

dac.write_dac(DAC_A, an.dac.v_ref) # Set DAC0 to full open
print('DAC_A to HIGH')

dac.write_dac(DAC_B, an.dac.v_ref) # Set DAC1 to full open
print('DAC_B to HIGH')

chan = ('1', '2')
tests = []

i = 0
while i < len(chan):
    tests.append(an.modSample()) # Create a new instance of modSample
    tests[i].newTest(chan[i]) # Create a new test instance under modSample
    prompt = raw_input("Activate test on channel {}? (Y/N)".format(chan[i])) # Prompt the user to select whether this test channel should be active
    if prompt == "Y":
        i += 1 # If Y, do nothing as the test instance is defaulted to be active
    elif prompt == "N":
        tests[i].active = False # If N, set the active flag to False
        i += 1
    else:
        print("Prompt only accepts Y or N") # If unknown input is entered, clear up the prompt, and re-start the loop with no increment

while True: # If either t1 or t2 still have cycles left, continue the test
<<<<<<< HEAD
    for i, value in enumerate(tests):
        if tests[i].active == True: # Check to see if the current test channel should be active, if it is then run through the tests
            pos = an.modMeasure(tests[i]) # Read inputs from the ADC
            an.posCheck(tests[i], pos) # Check input states against the setpoints
            an.logCheck(tests[i]) # See if it's time to log data to a csv
=======
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
>>>>>>> upstream/master
        else:
            pass
    state = False # Create a variable initialized to False
    for i, value in enumerate(tests):
        state = state | tests[i].active # Do a piecewise OR with each test.active state
    if state == False: # If all tests are inactive, it's time to shut it down
        False # Should exit the main while loop
    else:
<<<<<<< HEAD
        pass
=======
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
>>>>>>> upstream/master

for i, value in enumerate(tests): # Log all data after test is completed
    an.logData(tests[i])

print('sacrificing IO daemons')

bash = "sudo killall pigpiod" 
process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

print('except')

