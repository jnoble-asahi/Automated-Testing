import os
import time
import wiringpi as wp
import pigpio as io # pigpio daemon
import sys
import subprocess
<<<<<<< Updated upstream
import Tconfigs as tcf 
import adc_dac_config as an 
import gcpConfigs as gcpc
=======
import Tfunctions as Tfun

from ADS1256_definitions import * #Configuration file for the ADC settings
import adc_dac_config as an
from pipyadc import ADS1256 #Library for interfacing with the ADC via Python
import gpiozero as gz #Library for using the GPIO with python

# Initialise Pi connection
#pi = io.pi()
#if not pi.connected: # exit script if no connection
    #print('Unnable to connect to pi')
    #exit()
>>>>>>> Stashed changes

# Start the pigpio daemon 
bash = "sudo pigpiod" 
process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

<<<<<<< Updated upstream
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
=======
# Declare pin outputs and inputs
wp.pinmode(25, OUTPUT) # Blue test running LED
wp.pinmode(38, OUTPUT) # Red fault LED
wp.pinmode(3, OUTPUT) # Brake control setpoint
wp.pinmode(4, INPUT) # Transducer signal

# Set Test setpoints
# Brake setpoint (VDC)
print('Enter brake VDC setpoint (0-10VDC)')
setpoint = -1
while True:
    setpoint = raw_input() # prompt user for 0-10 VDC brake setpoint
    # check if setpoint is valid
    if setpoint >= 0 & <= 10:
>>>>>>> Stashed changes
        break
    
    print('Add new test on {}? (yes/no) '.format(chan[i]))
    prompt = raw_input() # prompt the user to see if they want to add a new test

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
        tcf.brakeOn(test[i-nos], setpoint) # Turn brake on to setpoint value
        i += 1 # Increment the test channel counter to track the number of active tests

    else:
        raise Warning('Something went wrong, check your work ') # If the test case isn't caught by the above, something's wrong
        tcf.warning_on()

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
<<<<<<< Updated upstream
        
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

  


=======
    else
        print('Invalid entry. Enter number greater than 0.')

# Start Test
wp.digitalWrite (25, HIGH) # Turn on test running light (blue)
wp.analogWrite(3, setpoint) # turn on brake
# turn on actuator
t = timegm() #test run start time

# Run and Record data
cycles = int(0) # number of completed actuator cycles
 data = [] #declare array for point data averages
# count cycles and end program once amount of cycles reached
while testLength > cycles:
   
    dataSample = [] # declare array for sample of data
    for x in range(10)
        p = wp.analogRead (4)
        dataSample.append(p)
    # Remove highest and lowest data points and average
    dataSample.remove(max(dataSample))
    dataSample.remove(min(dataSample))
    dataPoint = Tfun.Average(dataSample)
    data.append(dataPoint)
    time.sleep(0.1)

    # *actuator controls - add 1 to cycles once 1 cycle is complete* For now, cycles = amount of data points
    cycles += 1
>>>>>>> Stashed changes
