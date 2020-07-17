"""This test is for testing AVA modulating and on/off actuators for test #2 and #3 (max torque and max current) of the AVA evaluation test series. No limit switches are used. 
Manual brake controls are used so that the torque is adjusted to get the max torque."""

import system_tools as st ### Need to dig through the libraries and see where gpio is called before daemons getting started
# Putting this at the top until I can sort that out
print('Starting test set-up')
st.start_daemons() #start the pigpio helper daemon

import os
import time
import sys

import pigpio as io # pigpio daemon
from pipyadc import ADS1256 #Library for interfacing with the ADC via Python

import gcpConfigs as gcpc
import Tconfigs as tcon
from ADS1256_definitions import * #Configuration file for the ADC settings

# ADS setup
ads = ADS1256()
ads.cal_self() 
astep = ads.v_per_digit

# Start with LEDs off
tc.warning_off()
tc.running_off()

# Set pin numbers for the relay channels
######################## Original Code and Function Definitions from the pipyadc library ################################################
EXT1, EXT2, EXT3, EXT4 = POS_AIN0|NEG_AINCOM, POS_AIN1|NEG_AINCOM, POS_AIN2|NEG_AINCOM, POS_AIN3|NEG_AINCOM
EXT5, EXT6, EXT7, EXT8 = POS_AIN4|NEG_AINCOM, POS_AIN5|NEG_AINCOM, POS_AIN6|NEG_AINCOM, POS_AIN7|NEG_AINCOM

INPUTS_ADDRESS = (EXT1, EXT2, EXT3, EXT4, EXT5, EXT6, EXT7, EXT8)

CH1_Loc = {'cntrl' : DAC_A,
           'torq' : INPUTS_ADDRESS[4]}

## Set up test
test = gcpf.define_test()
test.create_on_off_test()
tcf.set_on_off(test, 1)

tc.running_on()

print('Adjust voltage to 10 to 15', '%', ' less than rated voltage.')
# Prompt user for when ready to continue
print("Enter 'g' when ready.")
ready = input()
while True:
    if ready == 'g':
        s = 0
        break
    else:
        print("Key not recognized. Enter 'g' when ready.")

stamp = time.time()
# Take torque measurements
try: 
    while True: 
        tor = torqueMeasurement(CH1_Loc['torq'])
        print(tor, ' in-lbs')
        test.torque.append(tor) # store torque reading measurement
        sleep(test.print_rate - 1) # subtract 1 to adjust for measurement time
        s += 1
        test.time.append(time.time()-stamp)
        if s % 10 == 0:
            test.update_db()
        else:
            pass
    except KeyboardInterrupt:
        test.update_db()
        break


print('Adjust voltage to rated voltage of actuator.')
# Prompt user for when ready to continue
print("Enter 'g' when ready.")
readyy = input()
while True:
    if readyy == 'g':
        s = 0
        break
    else:
        print("Key not recognized. Enter 'g' when ready.")

# Take torque measurements
try: 
    while True: 
        tor = torqueMeasurement(CH1_Loc['torq'])
        print(tor, ' in-lbs')
        test.torque.append(tor) # store torque reading measurement
        sleep(test.print_rate - 1) # subtract 1 to adjust for measurement time
        s += 1
        test.time.append(time.time()-stamp)
        if s % 10 == 0:
            test.update_db()
        else:
            pass
    except KeyboardInterrupt:
        test.update_db()
        break


print('Adjust voltage to 10 to 15', '%', ' above the rated voltage.')
# Prompt user for when ready to continue
print("Enter 'g' when ready.")
readyyy = input()
while True:
    if readyyy == 'g':
        s = 0
        break
    else:
        print("Key not recognized. Enter 'g' when ready.")

# Take torque measurements
try: 
    while True: 
        tor = torqueMeasurement(CH1_Loc['torq'])
        print(tor, ' in-lbs')
        test.torque.append(tor) # store torque reading measurement
        sleep(test.print_rate - 1) # subtract 1 to adjust for measurement time
        s += 1
        test.time.append(time.time()-stamp)
        if s % 10 == 0:
            test.update_db()
        else:
            pass
    except KeyboardInterrupt:
        test.update_db()
        break

# Power down
tc.shut_down(test)
st.killDaemons()

print("Test exited with a clean status, shut down by user")

