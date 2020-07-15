"This test is for testing AVA modulating and on/off actuators for test #2 of the AVA evaluation test series. No limit switches are used."

import system_tools as st ### Need to dig through the libraries and see where gpio is called before daemons getting started
# Putting this at the top until I can sort that out
print('Starting test set-up')
st.start_daemons() #start the pigpio helper daemon

import os
import time
import sys

import pigpio as io # pigpio daemon
from pipyadc import ADS1256 #Library for interfacing with the ADC via Python
import gpiozero as gz #Library for using the GPIO with python
import pandas as pd
import RPi.GPIO as GPIO # Using GPIO instead of wiringpi for reading digital inputs

import gcpConfigs as gcpc
from ADS1256_definitions import * #Configuration file for the ADC settings
import dac8552.dac8552 as dac1
from dac8552.dac8552 import DAC8552, DAC_A, DAC_B, MODE_POWER_DOWN_100K #Library for using the DAC

# DAC/ADS setup
ads = ADS1256()
ads.cal_self() 
astep = ads.v_per_digit
dac = DAC8552()
dac.v_ref = 5
step = dac.digit_per_v

dac.write_dac(DAC_A, 0*dac.digit_per_v) # Set DAC0
print('DAC_A to LOW')

dac.write_dac(DAC_B, 0*dac.digit_per_v) # Set DAC1
print('DAC_B to LOW')

# Set pin numbers for the relay channels
######################## Original Code and Function Definitions from the pipyadc library ################################################
EXT1, EXT2, EXT3, EXT4 = POS_AIN0|NEG_AINCOM, POS_AIN1|NEG_AINCOM, POS_AIN2|NEG_AINCOM, POS_AIN3|NEG_AINCOM
EXT5, EXT6, EXT7, EXT8 = POS_AIN4|NEG_AINCOM, POS_AIN5|NEG_AINCOM, POS_AIN6|NEG_AINCOM, POS_AIN7|NEG_AINCOM

INPUTS_ADDRESS = (EXT1, EXT2, EXT3, EXT4, EXT5, EXT6, EXT7, EXT8)

CH1_Loc = {'cntrl' : DAC_A,
           'torq' : INPUTS_ADDRESS[4],
           'FK_On': 6,
           'FK_Off' : 19} # GPIO pin numbers

## Set up test
print('Add test locally or remote? (local/remote)')
prompt = input() # prompt the user to see if they want to add a new test

HIGH = st.binary['HIGH']
LOW = st.binary['LOW']

responses = ('local', 'remote', 'exit')
'''
To start up the test, users are given an option to either pull parameters from a local JSON file, or from parameters stored in our GCP database

Test definitions and the steps to get there are laid out in the gcp_configs file
'''
while True: 
    if prompt not in responses:
        print('Input error, please enter local, remote, or exit')
        tc.warning_on()
    
    elif prompt == 'local':
        tc.warning_off()
        # Do some stuff to load test parameters locally
        break

    elif prompt == 'remote':
        test = gcpf.define_test()
        test.create_on_off_test()
        tcf.set_on_off(test, 1)
        tc.warning_off()
        break

    elif prompt == 'exit':
        tc.warning_off()
        break

    else:
        tc.warning_on()
        tc.shut_down(test)
        st.killDaemons()
        raise Warning ("Something went wrong, check your work")
