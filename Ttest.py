import os
import time
import sys
import subprocess

import wiringpi as wp
print ('hi 1')
import pigpio as io # pigpio daemon
from pipyadc import ADS1256 #Library for interfacing with the ADC via Python
import gpiozero as gz #Library for using the GPIO with python

import Tconfigs as tcf 
import adc_dac_config as an 
import gcpConfigs as gcpc
from ADS1256_definitions import * #Configuration file for the ADC settings


# Start the pigpio daemon 
print ('hi 2')
bash = "sudo pigpiod" 
process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
print('hi 3') # debugging
output, error = process.communicate()
time.sleep(3) # debugging
print('hi 4') #debugging


# Set pin numbers for the relay channels and the limit switch inputs
# Note that the pin numbers here follow the wiringPI scheme, which we've setup for *.phys or the GPIO header locations
# Since the wiringpi module communicates through the GPIO, there shouldn't be a need to initiate the SPI bus connection

chan = ('1', '2')
tests = []
i = 0
nos = 0
yes = ('YES', 'yes', 'y', 'Ye', 'Y')
no = ('NO','no', 'n', 'N', 'n')
yes_no = ('YES', 'yes', 'y', 'Ye', 'Y', 'NO','no', 'n', 'N', 'n')

print('Starting test set-up')

tcf.set_LEDs() # Declare pins connected to relays as digital outputs

# Make sure LEDs are off to start
tcf.warning_off() 
tcf.running_off()

while True:
    if (i >= len(chan)): # exit the loop if the test channels are full
        break
    
    print('Add new test on {}? (yes/no) '.format(chan[i]))
    prompt = input() # prompt the user to see if they want to add a new test

    if prompt not in yes_no: # If the input isn't recognized, try again
        print('Input error, please enter yes or no ')
        tcf.warning_on()

    elif prompt in no: # If they enter no, exit the loop
        tcf.warning_off()
        i += 1
        nos += 1

    elif prompt in yes: # If they answer yes, run the test creation functions
        tcf.warning_off()
        tests.append(gcpc.define_test()) # Creates a new gcp test class
        tests[i-nos].create_on_off_test() # Loads the test parameters
        tests[i-nos].parameter_check() # Checks that the parameters are within normal working ranges
        tcf.set_on_off(tests[i-nos], (i + nos)) # Sets up the IO pins to work for torque tests
        setpoint = tests[i-nos].convertSig() # Convert torque value (in-lbs) to 0-5vdc signal for pi
        tcf.brakeOn((i-nos), setpoint) # Turn brake on to setpoint value
        i += 1 # Increment the test channel counter to track the number of active tests

    else:
        tcf.warning_on()
        raise Warning('Something went wrong, check your work ') # If the test case isn't caught by the above, something's wrong

wait = 0.5 # A small waiting period is necessary, otherwise the switch input reads each cycle multiple times
tcf.running_on() # Turn on test running LED
stamp = time.time()

while True: # Start a loop to run the torque tests
    for i, value in enumerate(tests): # Loop through each test class one by one

        if ((time.time() - stamp) < (wait)): # Check to see if it's time to check the switch inputs again
            pass

        elif tests[i].active != True: # Check to see if the test is still active
            pass

        else: 
            tcf.switchCheck(tests[i], tests[i].input_channel) # Run a check of the current switch state, add 1 to pv if valid
            tcf.logCheck(tests[i]) # Check to see if it's time to log data
            stamp = time.time()

    state = False
    for i, value in enumerate(tests): # Loop through each test class and see if they're all inactive
        state = (state | tests[i].active)

    if state == False: # If all the test states are inactive, exit the loop
        break
        
    else:
        pass

for i, value in enumerate(tests[i]): # Log each test data one by one
    tests[i].update_db()
    
tcf.running_off() # Turn off test running LED

print('sacrificing IO daemons') # Kill the IO daemon process

bash = "sudo killall pigpiod" 
process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
output, error = process.communicate()


print("Test exited with a clean status")

  


