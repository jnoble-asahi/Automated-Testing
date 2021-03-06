# This program is for testing the Adafruit Analog Output K-type Thermocouple Amplifier with the Raspberry Pi and as well as the current sensor with the Raspberry Pi.

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


def measure_temp(pin):
    '''Takes voltage measurement and calculates the temperature.
    '''
    t = time.time()-t_start
    raw_channels = ads.read_oneshot(pin)
    voltage = float(raw_channels*astep)
    c_temp = (voltage - 1.25)/0.005  # Celsius
    f_temp = (c_temp*9/5) + 32  # Fahrenheit
    print('voltage (V):', voltage, 'temp (F):', f_temp)
    return(t, voltage)

def measure_current(pin):
    '''Takes voltage measurement and calculates the current.
    '''
    t = time.time()-t_start
    raw_channels = ads.read_oneshot(pin)
    voltage = float(raw_channels*astep)
    current = (voltage-2.6088)/0.0669  # 0.0669V per Amp. 0 A = 2.6088 V (experimental values)
    print('voltage (V): ', voltage, 'current (A): ', current)
    return(voltage)

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
t_start = time.time()
inp = EXT1  # Specify input pin
data_array = []
print('Measuring')
for x in range(0, 50):
    #measure_temp(inp)  # commented out because measuring current right now
    data_point = measure_current(inp)
    data_array.append(data_point)
    time.sleep(0.5)
    x =+ 1
# Calculate average 
n = len(data_array)
average = sum(data_array)/n
high = max(data_array)
low = min(data_array)
print('Average voltage: ', average)
print('Low: ', low, ' High: ', high)

killDaemons()
    