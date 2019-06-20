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
tests = onf.onOffTests

# Set pin numbers for the relay channels and the limit switch inputs
# Note that the pin numbers here follow the wiringPI scheme, which we've setup for *.phys or the GPIO header locations
# Since the wiringpi module communicates through the GPIO, there shouldn't be a need to initiate the SPI bus connection

onf.createTest() # Call the function that creates the tests given parameters

while True: # Start a loop to run the on/off tests
    for i, value in enumerate(onf.onOffTests): # Loop through each test class one by one
        if onf.onOffTests[i].active == True: # Check to see if the test is still active
            onf.switchCheck(onf.onOffTests[i], onf.onOffTests[i].input) # Run a check of the current switch state
            onf.cycleCheck(onf.onOffTests[i]) # Run a check on the cycle state, do stuff based on the this function
            onf.logCheck(onf.onOffTests[i]) # Check to see if it's time to log data
        else:
            pass # If the state of that test is inactive, do nothing
    state = False
    for i, value in enumerate(onf.onOffTests): # Loop through each test class and see if they're all inactive
        state = (state | onf.onOffTests[i].active)

    if state == False: # If all the test states are inactive, exit the loop
        False
    else:
        pass

for i, value in enumerate(onf.onOffTests): # Log each test data one by one
    onf.logData(onf.onOffTests[i])

print('sacrificing IO daemons') # Kill the IO daemon process

bash = "sudo killall pigpiod" 
process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

print("test exited with a clean status")