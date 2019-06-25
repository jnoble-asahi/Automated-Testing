'''
Refactor by pushing all test code into a single function that gets called once per loop
'''

############################################
''' This is a rough draft of code required to run the actuation tester prototype
Full details on dependencies and set-up instructions on Github here: exampleURL.com
Pin callouts in this program refer to the wiringPI addresses and not GPIO pin numbers
This script written by Chris May - pezLyfe on github
######## '''
import os
import time
import wiringpi as wp 
import pigpio as io
import sys
import math as mt
import numpy as np
import pandas as pd 
import onOffConfigs as onf 
import adc_dac_config as an 
import subprocess

# Start the pigpio daemon 
bash = "sudo pigpiod" 
process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

print('configuring test parameters')

# Set pin numbers for the relay channels and the limit switch inputs
# Note that the pin numbers here follow the wiringPI scheme, which we've setup for *.phys or the GPIO header locations
# Since the wiringpi module communicates through the GPIO, there shouldn't be a need to initiate the SPI bus connection

chan = ('1', '2', '3')
tests = []

for i, value in enumerate(chan):
    tests.append(onf.on_off())
    onf.createTest(tests[i], chan[i])

while True: # Start a loop to run the on/off tests
    for i, value in enumerate(tests): # Loop through each test class one by one
        if tests[i].active == True: # Check to see if the test is still active
            onf.switchCheck(tests[i], tests[i].input) # Run a check of the current switch state
            onf.cycleCheck(tests[i]) # Run a check on the cycle state, do stuff based on the this function
            onf.logCheck(tests[i]) # Check to see if it's time to log data
        else:
            pass # If the state of that test is inactive, do nothing
    state = False
    for i, value in enumerate(tests): # Loop through each test class and see if they're all inactive
        state = (state | tests[i].active)

    if state == False: # If all the test states are inactive, exit the loop
        False
    else:
        pass

for i, value in enumerate(tests): # Log each test data one by one
    onf.logData(tests[i])

print('sacrificing IO daemons') # Kill the IO daemon process

bash = "sudo killall pigpiod" 
process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

print("test exited with a clean status")