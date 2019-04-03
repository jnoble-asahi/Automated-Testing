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
#import wiringPi as wp 
import sys
import math as mt
import numpy as np
#from dac8552 import DAC8552, DAC_A, DAC_B, MODE_POWER_DOWN_100K #Libraries for using the DAC via SPi bus and pigpio module
from ADS1256_definitions import * #Libraries for using the ADC via the SPi bus and wiringPi module
from pipyadc import ADS1256
import gpiozero as gz 

######################## Original Code and Function Definitions from the pipyadc library ################################################
###  STEP 0: CONFIGURE CHANNELS AND USE DEFAULT OPTIONS FROM CONFIG FILE: ###
#
# For channel code values (bitmask) definitions, see ADS1256_definitions.py.
# The values representing the negative and positive input pins connected to
# the ADS1256 hardware multiplexer must be bitwise OR-ed to form eight-bit
# values, which will later be sent to the ADS1256 MUX register. The register
# can be explicitly read and set via ADS1256.mux property, but here we define
# a list of differential channels to be input to the ADS1256.read_sequence()
# method which reads all of them one after another.
#
# ==> Each channel in this context represents a differential pair of physical
# input pins of the ADS1256 input multiplexer.
#
# ==> For single-ended measurements, simply select AINCOM as the negative input.
#
# AINCOM does not have to be connected to AGND (0V), but it is if the jumper
# on the Waveshare board is set.
# The other external input screw terminals of the Waveshare board:
EXT1, EXT2, EXT3, EXT4 = POS_AIN0|NEG_AINCOM, POS_AIN1|NEG_AINCOM, POS_AIN2|NEG_AINCOM, POS_AIN3|NEG_AINCOM
EXT5, EXT6, EXT7, EXT8 = POS_AIN4|NEG_AINCOM, POS_AIN5|NEG_AINCOM, POS_AIN6|NEG_AINCOM, POS_AIN7|NEG_AINCOM

# Specify here an arbitrary length list (tuple) of arbitrary input channel pair
# eight-bit code values to scan sequentially from index 0 to last.
# Eight channels fit on the screen nicely for this example..
CH_SEQUENCE = (EXT1, EXT2, EXT3, EXT4, EXT5, EXT6, EXT7)
################################################################################


def do_measurement():
    ### STEP 1: Initialise ADC object using default configuration:
    # (Note1: See ADS1256_default_config.py, see ADS1256 datasheet)
    # (Note2: Input buffer on means limited voltage range 0V...3V for 5V supply)
    ads = ADS1256()

    ### STEP 2: Gain and offset self-calibration:
    ads.cal_self()

    while True:
        ### STEP 3: Get data:
        raw_channels = ads.read_sequence(CH_SEQUENCE)
        voltages     = [i * ads.v_per_digit for i in raw_channels]

        ### STEP 4: DONE. Have fun!
        nice_output(raw_channels, voltages)

### END EXAMPLE ###


#############################################################################
# Format nice looking text output:
def nice_output(digits, volts):
    sys.stdout.write(
          "\0337" # Store cursor position
        +
"""
These are the raw sample values for the channels:
Poti_CH0,  LDR_CH1,     AIN2,     AIN3,     AIN4,     AIN7, Poti NEG, Short 0V
"""
        + ", ".join(["{: 8d}".format(i) for i in digits])
        +
"""

These are the sample values converted to voltage in V for the channels:
Poti_CH0,  LDR_CH1,     AIN2,     AIN3,     AIN4,     AIN7, Poti NEG, Short 0V
"""
        + ", ".join(["{: 8.3f}".format(i) for i in volts])
        + "\n\033[J\0338" # Restore cursor position etc.
    )


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

    #elif currentTime - cycleStart < actTime:
    #    switch = gz.Button(5)
    #    if switch.is_pressed:
    #        print('Position Confirmed, ', 'Cycle count is ', test1)
    #        test1 += 1
    #    else:
    #        time.sleep(0.1)
    else:
        left = 10/.75 - (time.time() - cycleStart)
        print('Actuator in Motion ', left, ' Seconds remaining')
        time.sleep(1)
    do_measurement()
print("except")
GPIO.cleanup()