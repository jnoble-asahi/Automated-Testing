############################################
''' This is a rough draft of code required to run the actuation tester prototype

The script loads two other programs - ADC_Script and DAC_Script

The project requires a large number of dependencies from other libraries

Full details on dependencies and set-up instructions on Github here: exampleURL.com

Pin callouts in this program refer to the wiringPI addresses and not GPIO pin numbers

This script written by Chris May - pezLyfe on github
######## '''
import os
import RPi.GPIO as GPIO
import time
import wiringPi as wp 
import sys
from dac8552 import DAC8552, DAC_A, DAC_B, MODE_POWER_DOWN_100K #Libraries for using the DAC via SPi bus and pigpio module
from ADS1256_definitions import * #Libraries for using the ADC via the SPi bus and wiringPi module
from pipyadc import ADS1256
import gpiozero as gz 

'''Define a bunch of globals that we'll need
'Use lists for input states and time differences so that tests can be scaled up/down easily'
inputStates = [] 'A list of the current input states'
isLast = [] 'A list of the input states during the previous function call'
isStart = [] 'A list of the epoch times where each pin transitioned from HIGH to LOW'
availableStations = 3 - t1Samp - t2Samp 'Number of available test stations is 3 - the stations assigned to other tests' 
stStatus = [] 'Show the status of each relay as available/taken'
'''
#def switchCheck(pins, delay):
#    '''Because we'll likely be using mechanical switches in the actuators we're testing, we need to de-bounce the switches before
#    counting a cycle input. We're using low active for the inputs (tied to GND)
#    This function tracks the state of the input during the last call and compares it against the current state of the input
#'''
#    for pins in inputStates:
#        if inputStates[pins] == LOW & isLast[pins] == HIGH: 'If the input is currently LOW and the last state was HIGH, the function logs the current epoch time as START'
#        isStart[pins] = time.time()
#        inputStates[pins] = LOW
#        elif inputStates[pins] == LOW & isLast[pins] == LOW: 'If the current state is LOW and the last state was LOW, compare the START time against the debounce delay'
#            if time.time() - isStart[pins] > delay: '- If the difference between the current time and the start time is greater than the delay, increment the cycle counter'
#            test1 += 1
#            else:
#            'do nothing' '- If the difference is less than the delay, do nothing'
#        elif inputStates[pins] == HIGH & isLast[pins] == LOW: 'If the current state is HIGH and the last state was LOW, reset the last state to HIGH'
#        isLast[pins] = HIGH 
#        elif inputStates[pins] == HIGH & isLAst[pins] == HIGH: 'If the current state is HIGH and the last state was HIGH, do nothing'
#        'do nothing'

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

'''
The following set-up code was taken from the Relay_Module example made by the creators of the RPi relay board by Waveshare
Declare ints for each relay channel to call later, declare the settings for the BCM and the mode of operation for the specific GPIO pins used with the relay module
'''

Relay_Ch1 = 26
Relay_Ch2 = 20
Relay_Ch3 = 21


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(Relay_Ch1,GPIO.OUT)
GPIO.setup(Relay_Ch2,GPIO.OUT)
GPIO.setup(Relay_Ch3,GPIO.OUT)

print("Setup The Relay Module is [success]")



''' Begin original code
'''
ch1Input = 5
actOut = Relay_Ch1
actTime = 10/0.75
actIn = ch1Input

test1 = 0

try:
    while True:
    #Start the test by turning on the relay
        GPIO.output(Relay_Ch1,GPIO.HIGH)
        pos = 'HIGH'
        print("Actuator Opening")
        time.sleep(0.1)
        cycleStart = time.time()
        while 1000 > test1:
            currentTime = time.time()
            if currentTime - cycleStart > actTime:
                if pos == 'HIGH':
                    GPIO.output(Relay_Ch1, GPIO.LOW)
                    pos = 'LOW'
                    cycleStart = time.time()
                    print('Actuator Closing')
                    time.sleep(0.1)
                elif pos == 'LOW':
                    GPIO.output(Relay_Ch1, GPIO.HIGH)
                    pos = 'HIGH'
                    cycleStart = time.time()
                    print('Actuator Opening')
                    time.sleep(0.1)
                else:
                    print('Error, what the fuck?')
                    pos = 'HIGH'
                    cycleStart = time.time()
                    time.sleep(0.1)

            elif currentTime - cycleStart < actTime:
                switch = Button(5)
                if switch.is_pressed:
                    print('Position Confirmed, ', 'Cycle count is ', test1)
                    test1 += 1
                else:
                    time.sleep(0.1)
            else:
                print('The fucking cycle timers arent working')
                time.sleep(0.1)
except:
	print("except")
	GPIO.cleanup()
