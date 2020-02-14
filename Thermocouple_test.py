# This program is for testing the Adafruit Analog Output K-type Thermocouple Amplifier with the Raspberry Pi.

import os
import time
import numpy as np

import pigpio as io 
import gpiozero as gz # Library for using GPIO with python
import RPi.GPIO as GPIO # For reading inputs
import pandas as pd
from pipyadc import ADS1256 # Library for interfacing with the ADC via Python
from ADS1256_definitions import * # Configuration file for the ADC settings
import subprocess


def measure(pin):
    '''Takes voltage measurement and appends it to array.
    '''
    t = time.time()-t_start
    raw_channels = ads.read_oneshot(pin)
    voltage = float(raw_channels*astep)
    t_data.append(t)
    v_data.append(voltage)
    c_temp = (voltage - 1.5)/0.005  # Celsius
    f_temp = (c_temp*9/5) + 32  # Fahrenheit
    print('v:', voltage, f_temp, 'Fahrenheit')
    return(t, voltage)

def killDaemons():
    ''' Kills the IO deamon process.
    '''
    print('sacrificing IO daemons')
    bash = "sudo killall pigpiod" 
    process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return (output, error)


# Original Code and Function Definitions from the pipyadc library
EXT1, EXT2, EXT3, EXT4 = POS_AIN0|NEG_AINCOM, POS_AIN1|NEG_AINCOM, POS_AIN2|NEG_AINCOM, POS_AIN3|NEG_AINCOM
EXT5, EXT6, EXT7, EXT8 = POS_AIN4|NEG_AINCOM, POS_AIN5|NEG_AINCOM, POS_AIN6|NEG_AINCOM, POS_AIN7|NEG_AINCOM

print('Setting up')
# Set Up
ads = ADS1256()
ads.cal_self()
astep = ads.v_per_digit
v_data = []
t_data = []
t_start = time.time()
inp = EXT1  # Specify pin used

print('Measuring')
for x in range(0, 50):
    measure(inp)
    time.sleep(0.5)
    x =+ 1

killDaemons()
    