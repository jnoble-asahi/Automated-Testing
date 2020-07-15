''' File for decogging the brake. This code assumes the brake controller gain is already set to 40. Written by Julia Noble.'''
import os
import time
import sys
import math as mt
import numpy as np
import subprocess

import gpiozero as gz # Library for using the GPIO with python
import pandas as pd
import RPi.GPIO as GPIO # Using GPIO instead of wiringpi for reading digital inputs
from pipyadc import ADS1256 #Library for interfacing with the ADC via Python
from ADS1256_definitions import * # Configuration file for the ADC settings
import dac8552.dac8552 as dac1
from dac8552.dac8552 import DAC8552, DAC_A, DAC_B, MODE_POWER_DOWN_100K # Library for using the DAC

# Start the pigpio daemon 
print('summoning IO daemons')
bash = "sudo pigpiod" 
process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

# DAC/ADS setup
ads = ADS1256()
ads.cal_self() 
astep = ads.v_per_digit
dac = DAC8552()
dac.v_ref = 5
step = dac.digit_per_v

######################## Original Code and Function Definitions from the pipyadc library ################################################
EXT1, EXT2, EXT3, EXT4 = POS_AIN0|NEG_AINCOM, POS_AIN1|NEG_AINCOM, POS_AIN2|NEG_AINCOM, POS_AIN3|NEG_AINCOM
EXT5, EXT6, EXT7, EXT8 = POS_AIN4|NEG_AINCOM, POS_AIN5|NEG_AINCOM, POS_AIN6|NEG_AINCOM, POS_AIN7|NEG_AINCOM

INPUTS_ADDRESS = (EXT1, EXT2, EXT3, EXT4, EXT5, EXT6, EXT7, EXT8)

CH1_Loc = {'cntrl' : DAC_A,
           'torq' : INPUTS_ADDRESS[0],
           'FK_On': 6,
           'FK_Off' : 19} # GPIO pin numbers

CH2_Loc = {'cntrl' : DAC_B,
           'torq' : INPUTS_ADDRESS[3],
           'FK_On': 13,
           'FK_Off' : 26} # GPIO pin numbers

CH_Out = {'1' : DAC_A ,
          '2' : DAC_B}

tests = ('1', '2')

test_channels = {0: CH1_Loc,
                 1: CH2_Loc}

INPUT = 0
OUTPUT = 1
LOW = 0
HIGH = 1

gain = 40 
channel = 0 

print('Gain set to 40 mA/V. Channel set to 0.')
print('Enter max brake setpoint since cogging (in-lbs)')
cont = float(input())
while True:
    if (cont > 6000) | (cont < 0) :
        print('Choose torque setpoint between 0 and 6000 in-lbs')
    else:
        break
print('Enter cycle time of actuator (s)')
cycletime = float(input())
while True:
    if (cycletime <= 0) :
        print('Enter a positive number greater than 0')
    else:
        break
print ('Enter delay time (length of time actuator takes to start moving after limit switch is tripped).')
delay = float(input())
while True:
    if (delay < 0) :
        print('Enter a positive number')
    else:
        break

GPIO.setmode(GPIO.BCM)
closed_switch = test_channels[channel]['FK_Off']
open_switch = test_channels[channel]['FK_On']
GPIO.setup(closed_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(open_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)

###########################################################
# Deubgging limit switches
'''last_closed_state = GPIO.input(closed_switch)
last_open_state = GPIO.input(open_switch)
closed_state = GPIO.input(closed_switch)
open_state = GPIO.input(open_switch)
print('closed' , closed_state)
print('open', open_state)

i = 0

while i < 1000:
    closed_state = GPIO.input(closed_switch)
    open_state = GPIO.input(open_switch)
    print('closed: ', closed_state)
    print('open: ', open_state)
    if (last_closed_state == HIGH) & (closed_state == LOW) & (open_state == HIGH): # actuator just closed
        print('closed' , closed_state)
        print('open', open_state)
        last_closed_state == LOW
        last_open_state == HIGH
        i+=1
        time.sleep(1)
    
    elif (last_closed_state == LOW) & (closed_state == HIGH) & (open_state == HIGH): # actuator is moving
        print('closed' , closed_state)
        print('open', open_state)
        last_closed_state == HIGH
        last_open_state == HIGH
        i+=1
        time.sleep(1)

    elif (last_open_state == HIGH) & (closed_state == HIGH) & (open_state == LOW): # actuator just opened
        print('closed' , closed_state)
        print('open', open_state)
        last_closed_state == HIGH
        last_open_state == LOW
        i+=1
        time.sleep(1)

    elif (last_open_state == LOW) & (closed_state == HIGH) & (open_state == HIGH): # actuator is moving
        print('closed' , closed_state)
        print('open', open_state)
        last_closed_state == HIGH
        last_open_state == HIGH
        i+=1
        time.sleep(1)'''
#######################################################################################

# store current switch states for later
open_switch = test_channels[channel]['FK_On']
closed_switch = test_channels[channel]['FK_Off']
open_last_state = GPIO.input(open_switch)
closed_last_state = GPIO.input(closed_switch)

def power_down(testindex):
    print('powering down dac')
    test = tests[testindex]
    dac.power_down(CH_Out[test], MODE_POWER_DOWN_100K)

def convertSig(control):
    # convert in/lbs control setpoint to current value for brake signal
    ftlbs = control/12.0 #desired brake torque in ftlbs
    mA = 8.6652e-11*ftlbs**5 - 1.1637e-7*ftlbs**4 + 5.9406e-5*ftlbs**3 - 0.013952*ftlbs**2 + 1.9321*ftlbs + 46.644 #mA needed for brake
    tenV = mA/gain # 0-10vdc signal
    fiveV = tenV/2.0 # 0-5vdc signal
    print ('Brake setpoint', control, 'in-lbs')
    return fiveV

def brakeOff(channelID, control):
    '''
    #power brake off gradually to avoid cogging
'''
    closed_switch = test_channels[channelID]['FK_Off']
    open_switch = test_channels[channelID]['FK_On']
    closed_state = GPIO.input(closed_switch)
    open_state = GPIO.input(open_switch)
    open_last_state = open_state # Store the last FK_On switch state in a temp variable
    closed_last_state = closed_state # Store the last FK_Off switch state in temp variable
    cntrl_channel = test_channels[channelID]['cntrl'] # DAC
    print ('Waiting for actuator to start cycle')

    print('closed state', closed_state) 
    print('open state', open_state)
    while True:
        closed_state = GPIO.input(closed_switch)
        open_state = GPIO.input(open_switch)
        if (open_last_state == LOW) & (open_state == HIGH) & (closed_state == HIGH): # if actuator just started to move
            print(closed_state) 
            print(open_state)
            time.sleep(delay)
            setpnt = convertSig(control)
            pnt = setpnt + 0.275 # in volts
            t = cycletime/25
            while pnt > 0.275:
                dac.write_dac(cntrl_channel, int(step*pnt))
                time.sleep(t)
                print(pnt) # debugging
                pnt = pnt - (setpnt + 0.275)/25
                print(pnt)
                open_last_state = HIGH
                closed_last_state = HIGH
            break
        elif (closed_last_state == LOW) & (closed_state == HIGH) & (open_state == HIGH): # if actuator just started to move
            print(closed_state) 
            print(open_state)
            time.sleep(delay)
            setpnt = convertSig(control)
            pnt = setpnt + 0.275 # in volts
            t = cycletime/25
            while pnt > 0.275:
                dac.write_dac(cntrl_channel, int(step*pnt))
                time.sleep(t)
                print(pnt) # debugging
                pnt = pnt - (setpnt + 0.275)/25
                print(pnt)
                open_last_state = HIGH
                closed_last_state = HIGH
            break
        elif (open_last_state == HIGH) & (open_state == LOW) & (closed_state == HIGH):
            open_last_state = LOW
            closed_last_state = HIGH
            print('change direction')
        elif (closed_last_state == HIGH) & (closed_state == LOW) & (open_state == HIGH):
            open_last_state = HIGH
            closed_last_state = LOW
            print('change direction')

    dac.write_dac(cntrl_channel, int(0))

brakeOff(channel, cont)
power_down(channel)
print('brake ', channel, 'powered off')

print('sacrificing IO daemons') # Kill the IO daemon process
bash = "sudo killall pigpiod" 
process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
output, error = process.communicate()