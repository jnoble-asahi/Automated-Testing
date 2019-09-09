import os
import time
import sys
import math as mt
import numpy as np
import wiringpi as wp
from ADS1256_definitions import * #Configuration file for the ADC settings
import adc_dac_config as an
from pipyadc import ADS1256 #Library for interfacing with the ADC via Python
import gpiozero as gz #Library for using the GPIO with python
import pandas as pd
import subprocess

print('summoning IO daemons')
bash = "sudo pigpiod" 
process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

ads = ADS1256()
ads.cal_self() 
######################## Original Code and Function Definitions from the pipyadc library ################################################
EXT1, EXT2, EXT3, EXT4 = POS_AIN0|NEG_AINCOM, POS_AIN1|NEG_AINCOM, POS_AIN2|NEG_AINCOM, POS_AIN3|NEG_AINCOM
EXT5, EXT6, EXT7, EXT8 = POS_AIN4|NEG_AINCOM, POS_AIN5|NEG_AINCOM, POS_AIN6|NEG_AINCOM, POS_AIN7|NEG_AINCOM

INPUTS_ADDRESS = (EXT1, EXT2, EXT3, EXT4, EXT5, EXT6, EXT7, EXT8)

wp.wiringPiSetupPhys()

CH1_Loc = {'pos' : INPUTS_ADDRESS[0],
           'cur' : INPUTS_ADDRESS[2],
           'temp' : INPUTS_ADDRESS[5],
           'relay' : 37,
           'input': 31}

CH2_Loc = {'pos' : INPUTS_ADDRESS[1],
           'cur' : INPUTS_ADDRESS[3],
           'temp' : INPUTS_ADDRESS[6],
           'relay' : 38,
           'input': 33}

CH3_Loc = {'pos' : INPUTS_ADDRESS[0],
           'cur' : INPUTS_ADDRESS[4],
           'temp' : INPUTS_ADDRESS[7],
           'relay' : 40,
           'input' : 35}

CH1_SEQUENCE = (CH1_Loc['pos'], CH1_Loc['cur'], CH1_Loc['temp']) #Position, Current, Temperature channels

CH2_SEQUENCE =  (CH2_Loc['pos'], CH2_Loc['cur'], CH2_Loc['temp']) #Position, Current, Temperature channels

CH3_SEQUENCE =  (CH3_Loc['pos'], CH3_Loc['cur'], CH3_Loc['temp']) #Position, Current, Temperature channels

input_sequence = {1 : CH1_SEQUENCE,
                 2 : CH2_SEQUENCE,
                 3 : CH3_SEQUENCE} 

test_channels = {1: CH1_Loc,
                 2: CH2_Loc,
                 3: CH3_Loc}

tests = ('1', '2', '3')

binary = {'INPUT' : 0,
          'OUTPUT': 1,
          'LOW' : 0,
          'HIGH' : 1}

OUTPUT = binary['OUTPUT']
INPUT = binary['INPUT']
LOW = binary['LOW']
HIGH = binary['HIGH']

def set_on_off(test, channelID):
        test.name = channelID
        test.active = True
        test.relay_channel = test_channels[channelID]['relay']
        test.input_channel = test_channels[channelID]['input']
        test.input_sequence = input_sequence[channelID]

        wp.pinMode(test.relay_channel, OUTPUT) # Declare the pins connected to relays as digital outputs
        wp.pinMode(test.input_channel, INPUT) # Declare the pins connected to limit switches as digital inputs
        wp.pullUpDnControl(test.input_channel, 2) # Set the input pins for pull up control
        wp.digitalWrite(test.relay_channel, HIGH) # Write HIGH to the relay pins to start the test
        print("Channel {} set HIGH".format(test.name))

def restCalc(length, dCycle):
    '''
    Calculate a new cycle time using the length of the last half cycle, and the duty cycle setting of the test 
    '''
    rest = float(length / (float(dCycle)/100))
    return(rest)

def switchCheck(test, switchInput):
    '''
    Read the state of the actuator limit switch input
    If it's changed, do some stuff, if it hasn't changed, then do nothing
    '''
    state = wp.digitalRead(switchInput) # Reads the current switch state
    last_state = test.last_state # Store the last switch state in a temp variable
    
    if (last_state == HIGH) & (state == LOW): # Check if the switch changed from HIGH to LOW 
        test.last_state = LOW #Reset the "last state" of the switch
        length = time.time() - test.cycle_start # Calculate the length of the last cycle
        
        if (length > (test.cycle_time*.25)):
            test.pv = test.pv + 1 # Increment the pv counter if the switch changed
            print("Switch {} confirmed".format(test.name))
        
        else:
            test.bounces = test.bounces + 1 # If the switch went LOW really quickly it's likely just a bounce. Increment the bounce counter
            print("Switch {} bounced".format(test.name))
        '''
        Reserved block to later add duty cycle calc functions
        '''
    
    elif (last_state == LOW) & (state == HIGH): 
        print("Switch {} changed".format(test.name))
        test.last_state = 1
    
    else:
        pass

def cycleCheck(test_channel):
    '''
    Run a series of checks against the current time, the relay states, and actuator information
    Do something based on the results of those checks

    Sensor measurements are taken on the close -> open cycle since that's the point where actuator loads are the highest
    '''
    if test_channel.active != True: # If the test channel isn't currently active, pass
        pass

    elif (test_channel.pv > test_channel.target): # Check to see if the current cycle count is less than the target
        test_channel.active = False # If the pv has been reached, set the channel to inactive

    elif (time.time() - test_channel.cycle_start) > (test_channel.cycle_time): # Check to see if the current cycle has gone past the cycle time
        
        if test_channel.chan_state == HIGH: # If both are yes, change the relay state, and update cycle parameters
            wp.digitalWrite(test_channel.relay_channel, LOW)
            test_channel.chan_state = LOW
            test_channel.cycle_start = time.time()
            print("actuator {} closing".format(test_channel.name))
            time.sleep(0.1)
        
        elif test_channel.chan_state == LOW: #If the actuator recently closed, change the relay state, then take some measurements
            wp.digitalWrite(test_channel.relay_channel, HIGH) 
            test_channel.chan_state = HIGH
            test_channel.cycle_start = time.time()
            test_channel.shot_count = test_channel.shot_count + 1
            print("Actuator {} opening".format(test_channel.name))
            x = an.onOff_measurement(test_channel.input_sequence)
            test_channel.currents.append(x[0])
            test_channel.temps.append(x[1])
        
        else:
            print("Something's done messed up") # If the switch states don't match the top two conditions, somehow it went wrong
            test_channel.chanState = LOW
            test_channel.cycleStart = time.time()
            time.sleep(0.1)

def logCheck(testChannel):
    if (time.time() - testChannel.last_log) < (testChannel.print_rate):
        pass
    
    elif testChannel.active == False:
        pass
    
    elif testChannel.active == True:
        testChannel.update_db()
        testChannel.last_log = time.time()
    
    else:
        raise Warning("You didn't catch all of the cases")
    








