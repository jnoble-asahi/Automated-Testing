import os
import time
import sys
import math as mt
import numpy as np
import subprocess
import system_tools as st

from pipyadc import ADS1256 #Library for interfacing with the ADC via Python
import gpiozero as gz #Library for using the GPIO with python
import pandas as pd
import RPi.GPIO as GPIO # Using GPIO instead of wiringpi for reading digital inputs

from ADS1256_definitions import * #Configuration file for the ADC settings
import dac8552.dac8552 as dac1
from dac8552.dac8552 import DAC8552, DAC_A, DAC_B, MODE_POWER_DOWN_100K #Library for using the DAC

# LED pins
red = st.digital_outputs[0] # Using wirinpi pin numbers
blue = st.digital_outputs[1] # Using wiringpi pin numbers

# Make sure LEDs are off to start
red.on() 
blue.on()

# DAC/ADS setup
ads = ADS1256()
ads.cal_self() 
astep = ads.v_per_digit
dac = DAC8552()
dac.v_ref = 5
step = dac.digit_per_v

OUTPUT, INPUT, HIGH, LOW = st.OUTPUT, st.INPUT, st.HIGH, st.LOW
CH1_Loc = st.CH1_Loc

def warning_on():
    red.off() # off function because LED is wired NO

def warning_off():
    red.on()

def running_on():
    blue.off() # off function because LED is wired NO

def running_off():
    blue.on()

def brakeOn(test):
        setpnt = test.convertSig()
        test.cntrl_channel = CH1_Loc['cntrl']
        dac.write_dac(test.cntrl_channel, int(setpnt * step)) # Set brake to desired value
        print('Brake set to', setpnt, 'V')

def convertSetPoint(test):
    #convert in/lbs control setpoint to current value for brake signal
    ftlbs = test.control/12.0 #desired brake torque in ftlbs
    mA = 8.6652e-11*ftlbs**5 - 1.1637e-7*ftlbs**4 + 5.9406e-5*ftlbs**3 - 0.013952*ftlbs**2 + 1.9321*ftlbs + 46.644 # mA needed for brake
    tenV = mA/test.gain # 0-10vdc signal
    fiveV = tenV/2.0 # 0-5vdc signal
    print ('Brake setpoint:', test.control, 'in-lbs, ', fiveV, "V/5V")
    return fiveV
    
def brakeChange(test, t):
    ftlbs = t/12.0 #desired brake torque in ftlbs
    mA = 8.6652e-11*ftlbs**5 - 1.1637e-7*ftlbs**4 + 5.9406e-5*ftlbs**3 - 0.013952*ftlbs**2 + 1.9321*ftlbs + 46.644 # mA needed for brake
    tenV = mA/test.gain # 0-10vdc signal
    fiveV = tenV/2.0 # 0-5vdc signal
    print ('Brake setpoint:', t, 'in-lbs, ', fiveV, "V/5V")
    test.cntrl_channel = CH1_Loc['cntrl']
    dac.write_dac(test.cntrl_channel, int(fiveV * step)) # Set brake to desired value
    print('Brake set to', fiveV, 'V')
    
def torqueMeasurement(input):
    # Collect 20 data point readings across 1 seconds
    setData = []
    for i in range (0, 25):
        raw_channels = ads.read_oneshot(input)
        time.sleep(0.04)
        setData.append(raw_channels)
    # Remove 6 max and min values
    for x in range(0,6):
        setData.remove(max(setData)) 
        setData.remove(min(setData))
    rawVal = float(sum(setData)/len(setData)) # Average everything else

    voltage = float(rawVal*astep) # Convert raw value to voltage
    print('voltage reading: ', voltage) # for troubleshooting/calibration
    torque = torqueConvert(voltage) # Convert voltage value to torque value
    print('torque reading: ', torque)
    return torque

def torqueConvert(volt):
    torqueVal = (volt - 2.5)*6000/2.5 #convert reading to torque value in in-lbs
    return(torqueVal)

def ttest_measures(test):
    for y in range (test.cycle_points):
        # wait 1/3 of cycle time or 1/cyclepoints
        while True:
            if (time.time() - test.cycle_start) > (((y)/test.cycle_points)*test.cycle_time):
                tor = torqueMeasurement(CH1_Loc['torq'])
                test.torque.append(tor) # store torque reading measurement
                # store other values
                # measure current at some interval
                # measure temperature at some interval
                test.time.append(time.time()-test.cycleStart)
            break

# prevents issues with shutdown (cogging etc) - for quarter turn actuator (change 25 for 50 for half turn)
def shut_down(test):
    running_off() # Turn off test running LED

    # Define channels
    cntrl_channel = CH1_Loc['cntrl'] # DAC
    open_switch = CH1_Loc['FK_On']
    closed_switch = CH1_Loc['FK_Off']

    #open_state = open_switch.value # Read limit switch
    #closed_state = closed_switch.value # Read limit switch
    #open_last_state = test.open_last_state # Store the last FK_On switch state in a temp variable
    #closed_last_state = test.closed_last_state # Store the last FK_Off switch state in temp variable

    #print('Waiting for actuator to start cycle.')
    #print('closed state', closed_state) 
    #print('open state', open_state)

    while True:
        setpnt = convertSetPoint(test)
        pnt = setpnt + 0.275 # in volts
        t = (test.cycle_time - 1)/25
        while pnt > 0.275:
            dac.write_dac(cntrl_channel, int(step*pnt))
            time.sleep(t)
            print(pnt) # debugging
            pnt = pnt - (setpnt + 0.275)/25
            open_last_state = HIGH
            closed_last_state = HIGH
        break
    '''
        closed_state = GPIO.input(closed_switch)
        open_state = GPIO.input(open_switch)
        if (open_last_state == LOW) & (open_state == HIGH) & (closed_state == HIGH): # if actuator just started to move
            print(closed_state) 
            print(open_state)
            time.sleep(test.delay)
            setpnt = convertSetPoint(test)
            pnt = setpnt + 0.275 # in volts
            t = (test.cycle_time - 1)/25
            while pnt > 0.275:
                dac.write_dac(cntrl_channel, int(step*pnt))
                time.sleep(t)
                print(pnt) # debugging
                pnt = pnt - (setpnt + 0.275)/25
                open_last_state = HIGH
                closed_last_state = HIGH
            break
        elif (closed_last_state == LOW) & (closed_state == HIGH) & (open_state == HIGH): # if actuator just started to move
            print(closed_state) 
            print(open_state)
            time.sleep(test.delay)
            setpnt = convertSetPoint(test)
            pnt = setpnt + 0.275 # in volts
            t = (test.cycle_time-1)/25
            while pnt > 0.275:
                dac.write_dac(cntrl_channel, int(step*pnt))
                time.sleep(t)
                print(pnt) # debugging
                pnt = pnt - (setpnt + 0.275)/25
                open_last_state = HIGH
                closed_last_state = HIGH
            break
        elif (open_last_state == HIGH) & (open_state == LOW) & (closed_state == HIGH): # actuator just stopped moving. wait until new cycle begins
            open_last_state = LOW
            closed_last_state = HIGH
            print('change direction')
        elif (closed_last_state == HIGH) & (closed_state == LOW) & (open_state == HIGH): # actuator just stopped moving. wait until new cycle begins
            open_last_state = HIGH
            closed_last_state = LOW
            print('change direction')
    '''
    print('Powering down DAC')
    dac.write_dac(cntrl_channel, int(0))
    #dac.power_down(CH_Out[test], MODE_POWER_DOWN_100K)
    warning_off()










