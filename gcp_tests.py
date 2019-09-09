import os
import time
import wiringpi as wp 
import pigpio as io
import sys
import test_configs as tcf 
import adc_dac_config as an 
import subprocess
import gcp_configs as gcpf

# Start the pigpio daemon 
bash = "sudo pigpiod" 
process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

# Set pin numbers for the relay channels and the limit switch inputs
# Note that the pin numbers here follow the wiringPI scheme, which we've setup for *.phys or the GPIO header locations
# Since the wiringpi module communicates through the GPIO, there shouldn't be a need to initiate the SPI bus connection

chan = ('1', '2', '3')
tests = []
i = 0
nos = 0
yes = ('YES', 'yes', 'y', 'Ye', 'Y')
no = ('NO','no', 'n', 'N', 'n')
yes_no = ('YES', 'yes', 'y', 'Ye', 'Y', 'NO','no', 'n', 'N', 'n')

print('starting test set-ups')

while True:
    if (i >= len(chan)): # exit the loop if the test channels are full
        break
    
    print('Add new test on {}? (yes/no) '.format(chan[i]))
    prompt = raw_input() # prompt the user to see if they want to add a new test

    if prompt not in yes_no: # If the input isn't recognized, try again
        print(' Input error, please enter yes or no ')

    elif prompt in no: # If they enter no, exit the loop
        i += 1
        nos += 1

    elif prompt in yes: # If they answer yes, run the test creation functions
        tests.append(gcpf.define_test()) # creates a new gcp test class
        tests[i-nos].create_on_off_test() # Loads the test parameters
        tests[i-nos].parameter_check() # Checks that the parameters are within normal working ranges
        tcf.set_on_off(tests[i-nos], (i + nos)) # Sets up the IO pins to work for on/off tests
        i += 1 # Increment the test channel counter to track the number of active tests

    else:
        raise Warning( 'Something went wrong, check your work ') # If the test case isn't caught by the above, something's wrong

wait = 0.5 # A small waiting period is necessary, otherwise the switch input reads each cycle multiple times

stamp = time.time()
while True: # Start a loop to run the on/off tests
    for i, value in enumerate(tests): # Loop through each test class one by one

        if ((time.time() - stamp) < (wait)): # Check to see if it's time to check the switch inputs again
            pass

        elif tests[i].active != True: # Check to see if the test is still active
            pass

        else: # Check to see if the test is still active
            tcf.switchCheck(tests[i], tests[i].input_channel) # Run a check of the current switch state
            tcf.cycleCheck(tests[i]) # Run a check on the cycle state, do stuff based on the this function
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

print('sacrificing IO daemons') # Kill the IO daemon process

bash = "sudo killall pigpiod" 
process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

print("test exited with a clean status")

