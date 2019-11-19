import os
import time
import sys
import math as mt
import numpy as np
import subprocess

import wiringpi as wp
from pipyadc import ADS1256 #Library for interfacing with the ADC via Python
import gpiozero as gz #Library for using the GPIO with python
import pandas as pd

from ADS1256_definitions import * #Configuration file for the ADC settings
import adc_dac_config as an
import dac8552.dac8552 as dac1
from dac8552.dac8552 import DAC8552, DAC_A, DAC_B, MODE_POWER_DOWN_100K #Library for using the DAC

print('summoning IO daemons')
bash = "sudo pigpiod" 
process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

ads = ADS1256()
ads.cal_self() 
dac = DAC8552()

######################## Original Code and Function Definitions from the pipyadc library ################################################
EXT1, EXT2, EXT3, EXT4 = POS_AIN0|NEG_AINCOM, POS_AIN1|NEG_AINCOM, POS_AIN2|NEG_AINCOM, POS_AIN3|NEG_AINCOM
EXT5, EXT6, EXT7, EXT8 = POS_AIN4|NEG_AINCOM, POS_AIN5|NEG_AINCOM, POS_AIN6|NEG_AINCOM, POS_AIN7|NEG_AINCOM

INPUTS_ADDRESS = (EXT1, EXT2, EXT3, EXT4, EXT5, EXT6, EXT7, EXT8)

wp.wiringPiSetupPhys()

CH1_Loc = {'cntrl' : DAC_A,
           'torq' : INPUTS_ADDRESS[0],
           'input': 31}

CH2_Loc = {'cntrl' : DAC_B,
           'torq' : INPUTS_ADDRESS[1],
           'input': 33}
'''
CH1_SEQUENCE = (CH1_Loc['cntrl'], CH1_Loc['torq'], CH1_Loc['pos']) # Torque, Current, Position channels

CH2_SEQUENCE =  (CH2_Loc['cntrl'], CH2_Loc['torq'], CH2_Loc['pos']) # Torque, Current, Position channels


input_sequence = {1 : CH1_SEQUENCE,
                 2 : CH2_SEQUENCE} 
'''
test_channels = {0: CH1_Loc,
                 1: CH2_Loc}

tests = ('1', '2')

binary = {'INPUT' : 0,
          'OUTPUT': 1,
          'LOW' : 0,
          'HIGH' : 1}

OUTPUT = binary['OUTPUT']
INPUT = binary['INPUT']
LOW = binary['LOW']
HIGH = binary['HIGH']

#LED pins
LED_F = 37
LED_T = 38
    
def set_LEDs():
    # Decalre pins connected to relays as digital outputs
    wp.pinMode(LED_F, OUTPUT)
    wp.pinMode(LED_T, OUTPUT)

def warning_on():
    wp.digitalWrite(LED_F, HIGH)

def warning_off():
    wp.digitalWrite(LED_F, LOW)

def running_on():
    wp.digitalWrite(LED_T, HIGH) # Write HIGH to the Test Running LED for starting test

def running_off():
    wp.digitalWrite(LED_T, LOW) # Write LOW to the Test Running LED for when test is not in progress

def set_on_off(test, channelID):
        test.name = channelID
        test.active = True
        test.cntrl_channel = test_channels[channelID]['cntrl']
        test.input_channel = test_channels[channelID]['input']
        test.output_channel = test_channels[channelID]['torq']
        #test.input_sequence = input_sequence[channelID]
        dac.write_dac(test.cntrl_channel, int(0 * dac.digit_per_v)) # Set brake to 0
        print('Brake set to 0')
        wp.pinMode(test.input_channel, INPUT) # Declare the pins connected to limit swithces as inputs
        wp.pinMode(test.output_channel, OUTPUT) # Declare the pin connected to torque transducer signal as an output
        wp.pullUpDnControl(test.input_channel, 2) # Set the input pins for pull up control

def brakeOn(channelID, setpnt):
        if setpnt not in range (0, 5):
            warning_on()
            raise ValueError('Brake control signal outside 0-5vdc')
        else:
            cntrl_channel = test_channels[channelID]['cntrl']
            dac.write_dac(cntrl_channel, int(setpnt * dac.digit_per_v)) # Set brake to desired value
            print('Brake set to', setpnt, 'V')

def restCalc(length, dCycle):
    '''
    Calculate a new cycle time using the length of the last half cycle, and the duty cycle setting of the test 
    '''
    rest = float(length / (float(dCycle)/100))
    return rest

def torqueMeasurement(inputs):
    '''
    Takes series of torque measurement readings and averages them
    '''
    raw_channels = ads.read_oneshot(inputs)

    # Collect 10 data point readings
    setData = []
    for i in range (0, 10):
        torSens = raw_channels
        setData.append(torSens)
    # Remove max and min values
    setData.remove(max(setData)) 
    setData.remove(min(setData))
    torSens = sum(setData)/len(setData) # Average everything else
    torqueVal = (torSens - 4)*6000/16 # Convert 4-20 mA indicator signal to torque reading in in-lbs
    return torqueVal

def switchCheck(test, switchInput):
    '''
    Read the state of the actuator limit switch input
    If it's changed, do some stuff, if it hasn't changed, then do nothing '''

    if test.active == True:
        if (testChannel.pv < testChannel.target): # Check to see if the current cycle count is less than the target
            pv = test.pv # set pv variable equal to current number of cycles completed
            torr = torqueMeasurement(test.output_channel) # collect torque data and average
            state = wp.digitalRead(switchInput) # Reads the current switch state
            last_state = test.last_state # Store the last switch state in a temp variable
            # Store other values
            test.cycleBounces.append(test.bounces)
            test.time.append(time.time()) 
            test.pv.append(pv)

            if (last_state == HIGH) & (state == LOW): # Check if the switch changed from HIGH to LOW 
                test.last_state = LOW #Reset the "last state" of the switch
                length = time.time() - test.cycle_start # Calculate the length of the last cycle
        
                if (length > (test.cycle_time*.25)):
                    pv+= 1 # Increment the pv counter if the switch changed
                    print("Switch {} confirmed".format(test.name))
                    test.torque.append(torr) # store torque reading measurement taken before if statement
                    test.cycleBounces.append(test.bounces)
                    test.time.append(time.time()) 
                    test.pv.append(pv)

                    # collect (cycle_points - 1) more points in cycle
                    for y in range (test.cycle_points - 1):
                        while True:
                            # wait 1/3 of cycle time or 1/cyclepoints
                        if (time.time() - test.cycle_start) > ((y+1)/test.cycle_points):
                                tor = torqueMeasurement(test.input_sequence)
                                test.torque.append(tor) # store torque reading measurement
                                # store other values
                                test.cycleBounces.append(test.bounces)
                                test.time.append(time.time()) 
                                test.pv.append(pv)
                                break
                else:
                    test.bounces = test.bounces + 1 # If the switch went LOW really quickly it's likely just a bounce. Increment the bounce counter
                    print("Switch {} bounced".format(test.name))
                '''
                Reserved block to later add duty cycle calc functions
                '''
    
            elif (last_state == LOW) & (state == HIGH): 
                print("Switch {} changed".format(test.name))
                test.last_state = HIGH
    
            else:
                pass
        else:
            test.active = False
    else:
        pass



'''
def onOff_measurement(inputs):

    # Read the input voltages from the current and brake control inputs on the ADC. 
    # Voltages are converted from raw integer inputs using convert functions in this library
    
    raw_channels = ads.read_sequence(inputs)
    cntrl = raw_channels[0]
    curr = raw_channels[1]
    return(contrl, curr)
 '''   

def logCheck(testChannel):
    if (time.time() - testChannel.last_log) < (testChannel.print_rate):
        pass
    
    elif testChannel.active == False:
        pass

    elif testChannel.active == True:
        testChannel.update_db()
        testChannel.last_log = time.time()
    
    else:
        warning_on()
        raise Warning("You didn't catch all of the cases")










