############################################
''' This is a rough draft of code required to run the actuation tester prototype
The script loads two other programs - ADC_Script and DAC_Script
The project requires a large number of dependencies from other libraries
Full details on dependencies and set-up instructions on Github here: exampleURL.com
Pin callouts in this program refer to the wiringPI addresses and not GPIO pin numbers
This script written by Chris May - pezLyfe on github
######## '''
import os
import time
import os
import wiringpi as wp 
import sys
print sys.path
import math as mt
import numpy as np

#def testAssign(chan, cycle_time, duty_cycle, actIn): 'It may make sense to initiate a class with all of the test parameters here'
#''' This function assigns the test parameters to the proper test stations.
#        Parameters can include:
#            - Relay channel
#            - ADC addresses (for temperature and current sensors)
#            - DAC addresses (if necessary for modulating outputs)
#            - The desired duty cycle
#            - The length of the test
#        Notice that this test station can run two modulating tests simultaneously with 3 on/off tests, so that's pretty baller
#            - Check the GPIO availability to make sure that's true
#    '''
#channel = chan 
#fullCycle = cycle_time / duty_cycle #calculate the test time based on duty cycle and actuator cycle time
#switchConf = actIn

#def relayCheck(variables)
#    '''This function will compare the amount of time that's passed since the last relay state change, and compare it against the required duty cycle
#      - If the time is longer than required by duty cycle
#            - Change the relay state
#            - Reset the time counter
#      - If the time is not longer than required by duty cycle
#            - Do nothing
#      - Iterate through all of the on/off test that are currently running
#    '''

#def modCheck(variables)
#    ''' This function will check whether the actuator has reached the required position
#    It does this by comparing the DAC output against the ADC input (For actuators with position tracking)
#    If the actuator doesn't have position tracking, we'll have to do something else
#    Store a moving average of the duty cycle of the actuator on random modulating positions
#        - If the duty cycle is too high, introduce a delay in the program
#    If the actuator is in the correct position, check how long it's been there fore
#        - If it's been long enough, set a new random position
#        - If it hasn't do nothing
#    '''

#def getADC(variables)
#    '''This function will call the ADC program from the PiPyADC library
#    results from the call will be stored in a couple of variables
#    If a lot of time has passed, then it's time to write the results to the SD card
#    '''

# Set pin numbers for the relay channels and the limit switch inputs
# Note that the pin numbers here follow the wiringPI scheme, which we've setup for *.phys or the GPIO header locations
# Since the wiringpi module communicates through the GPIO, there shouldn't be a need to initiate the SPI bus connection
wp.wiringPiSetupPhys()

INPUT = 0
OUTPUT = 1
LOW = 0
HIGH = 1

Relay_Ch1 = 37
Relay_Ch2 = 38
Relay_Ch3 = 40
ch1_in = 31

wp.pinMode(Relay_Ch1, OUTPUT)
wp.pinMode(Relay_Ch2, OUTPUT)
wp.pinMode(Relay_Ch3, OUTPUT)

wp.pinMode(ch1_in, INPUT)
print("Relay Module Set-up")

actIn = ch1_in
actOut = Relay_Ch1
actTime = 10/0.75
        
# Start the test by turning on the relay
wp.digitalWrite(actOut, HIGH)
pos = 'HIGH'
print("Actuator Opening")
time.sleep(0.1)
cycleStart = time.time()
test1 = 0

# GPIO inputs are low active (we're tying inputs to GND), so a low input to the GPIO should read as a switch confirmation

while 1000 > test1:
    currentTime = time.time()
    if currentTime - cycleStart > actTime:
        if pos == 'HIGH':
            wp.digitalWrite(actOut, LOW)
            pos = 'LOW'
            cycleStart = time.time()
            print('Actuator Closing')
            time.sleep(0.1)
        elif pos == 'LOW':
            wp.digitalWrite(actOut, HIGH)
            pos = 'HIGH'
            cycleStart = time.time()
            print('Actuator Opening')
            time.sleep(0.1)
        else:
            print('Error, what did you do?')
            pos = 'HIGH'
            cycleStart = time.time()
            time.sleep(0.1)
    elif currentTime - cycleStart < actTime:
        switchState = wp.digitalRead(actIn)
        if switchState == LOW:
            print('switch is closed')
            time.sleep(1)
        elif switchState == HIGH:
            print('switch is open')
            time.sleep(1)
        else:
            print("switch unknown, do you know what you're doing?")
            time.sleep(1)
print("except")
GPIO.cleanup()