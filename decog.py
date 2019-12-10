''' File for decogging the brake. gain of 40'''
import os
import time
import sys
import math as mt
import numpy as np
import subprocess

import gpiozero as gz #Library for using the GPIO with python
import pandas as pd
import RPi.GPIO as GPIO # Using GPIO instead of wiringpi for reading digital inputs

from ADS1256_definitions import * #Configuration file for the ADC settings
import dac8552.dac8552 as dac1
from dac8552.dac8552 import DAC8552, DAC_A, DAC_B, MODE_POWER_DOWN_100K #Library for using the DAC

# Start the pigpio daemon 
print('summoning IO daemons')
bash = "sudo pigpiod" 
process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

######################## Original Code and Function Definitions from the pipyadc library ################################################
EXT1, EXT2, EXT3, EXT4 = POS_AIN0|NEG_AINCOM, POS_AIN1|NEG_AINCOM, POS_AIN2|NEG_AINCOM, POS_AIN3|NEG_AINCOM
EXT5, EXT6, EXT7, EXT8 = POS_AIN4|NEG_AINCOM, POS_AIN5|NEG_AINCOM, POS_AIN6|NEG_AINCOM, POS_AIN7|NEG_AINCOM

INPUTS_ADDRESS = (EXT1, EXT2, EXT3, EXT4, EXT5, EXT6, EXT7, EXT8)

CH1_Loc = {'cntrl' : DAC_A,
           'torq' : INPUTS_ADDRESS[0],
           'FK_On': 6,
           'FK_Off' : 13} #GPIO pin numbers

CH2_Loc = {'cntrl' : DAC_B,
           'torq' : INPUTS_ADDRESS[3],
           'FK_On': 19,
           'FK_Off' : 26} #GPIO pin numbers

CH_Out = {'1' : DAC_A ,
          '2' : DAC_B}

tests = ('1', '2')

test_channels = {0: CH1_Loc,
                 1: CH2_Loc}

gain = 40 
channel = 0 
cont = 600 # highest brake setpoint since it started cogging (in-lbs)

time.time(2) #debug

# DAC setup
dac = DAC8552()
dac.v_ref = 5
step = dac.digit_per_v

def power_down(testindex):
    print('powering down dac')
    test = tests[testindex]
    dac.power_down(CH_Out[test], MODE_POWER_DOWN_100K)

def convertSig(control):
    #convert in/lbs control setpoint to current value for brake signal
        ftlbs = control/12.0 #desired brake torque in ftlbs
        if ftlbs <= 10:
            fiveV = 0
            print('Brake setpoint set to minimum torque of 120 in-lbs')
        else: 
            mA = 8.6652e-11*ftlbs**5 - 1.1637e-7*ftlbs**4 + 5.9406e-5*ftlbs**3 - 0.013952*ftlbs**2 + 1.9321*ftlbs + 46.644 #mA needed for brake
            tenV = mA/gain #0-10vdc signal
            fiveV = tenV/2.0 #0-5vdc signal
            print ('Brake setpoint', control, 'in-lbs')
        return fiveV

def brakeOn(channelID, control):
        setpnt = convertSig(control)
        cntrl_channel = test_channels[channelID]['cntrl']
        dac.write_dac(cntrl_channel, int(setpnt * step)) # Set brake to desired value
        print('Brake set to', setpnt, 'V')

def brakeOff(channelID, control):
    '''
    power brake off gradually to avoid cogging
    '''
    setpnt = convertSig(control)
    cntrl_channel = test_channels[channelID]['cntrl']
    pnt = setpnt + 0.275 # in volts
    while pnt > 0.11:
        dac.write_dac(cntrl_channel, int(step*pnt))
        print(pnt) # debugging
        time.sleep(0.1)
        pnt = pnt - 0.11
    power_down(channelID)
    print('brake ', channelID, 'powered off')

#brakeOn(channel, cont)
brakeOff(channel, cont)

print('sacrificing IO daemons') # Kill the IO daemon process
bash = "sudo killall pigpiod" 
process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
output, error = process.communicate()