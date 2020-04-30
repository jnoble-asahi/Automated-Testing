import system_tools as st ### Need to dig through the libraries and see where gpio is called before daemons getting started
# Putting this at the top until I can sort that out
print('Starting test set-up')
st.start_daemons() #start the pigpio helper daemon

import os
import time
import gpiozero as gz
import pigpio as io

from pipyadc import ADS1256 #Library for interfacing with the ADC via Python
from ADS1256_definitions import * #Configuration file for the ADC settings

import test_configs as tcf 
import Tconfigs as tc
import gcpConfigs as gcpf

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

wait = 0.5 # A small waiting period is necessary, otherwise the switch input reads each cycle multiple times
print('Running test(s)')
tc.running_on() # Turn on test running LED
stamp = time.time()

tc.brakeOn(test)

try: 
    while True: # Start a loop to run the torque tests
        if ((time.time() - stamp) < (wait)): # Check to see if it's time to check the switch inputs again
            pass

        elif test.active != True: # Check to see if the test is still active
            break

        else: 
            #tcf.switchCheck(test) # Run a check of the current switch state, add 1 to pv if valid
            tcf.cycleCheck(test)
            tcf.logCheck(test) # Check to see if it's time to log data
            stamp = time.time()
            
except KeyboardInterrupt:
    test.update_db()

    # Power down
    tc.shut_down(test)
    st.killDaemons()

    print("Test exited with a clean status, shut down by user")

test.update_db()

# Power down
tc.shut_down(test)
st.killDaemons()

print("Test exited with a clean status")


    

