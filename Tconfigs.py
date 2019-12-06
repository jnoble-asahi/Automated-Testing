import os
import time
import sys
import math as mt
import numpy as np
import subprocess

from pipyadc import ADS1256 #Library for interfacing with the ADC via Python
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

# LED pins
red = gz.LED(26) # Using wirinpi pin numbers
blue = gz.LED(20) # Using wiringpi pin numbers

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

'''
CH1_SEQUENCE = (CH1_Loc['cntrl'], CH1_Loc['torq'], CH1_Loc['pos']) # Torque, Current, Position channels

CH2_SEQUENCE =  (CH2_Loc['cntrl'], CH2_Loc['torq'], CH2_Loc['pos']) # Torque, Current, Position channels


input_sequence = {1 : CH1_SEQUENCE,
                 2 : CH2_SEQUENCE} 
'''
test_channels = {0: CH1_Loc,
                 1: CH2_Loc}

binary = {'INPUT' : 0,
          'OUTPUT': 1,
          'LOW' : 0,
          'HIGH' : 1}

OUTPUT = binary['OUTPUT']
INPUT = binary['INPUT']
LOW = binary['LOW']
HIGH = binary['HIGH']

def warning_on():
    red.off() # off function because LED is wired NO

def warning_off():
    red.on()

def running_on():
    blue.off() # off function because LED is wired NO

def running_off():
    blue.on()

def set_on_off(test, channelID):
        test.name = channelID
        test.active = True
        print('Reseting variable values in the cloud')
        test.bounces = 0
        test.torque = []
        test.pv = 0
        test.cntrl_channel = test_channels[channelID]['cntrl']
        test.input_channel = test_channels[channelID]['FK_On']
        test.input_off_channel = test_channels[channelID]['FK_Off']
        test.output_channel = test_channels[channelID]['torq']
        print('setting dac')
        dac.write_dac(test.cntrl_channel, 0*step) # Set brake to 0
        print('Brake set to 0.')
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # store current switch states for later
        open_switch = test_channels[channelID]['FK_On']
        closed_switch = test_channels[channelID]['FK_Off']
        test.open_last_state = GPIO.input(open_switch)
        test.closed_last_state = GPIO.input(closed_switch)

def brakeOn(test, channelID):
        setpnt = test.convertSig()
        test.cntrl_channel = test_channels[channelID]['cntrl']
        dac.write_dac(test.cntrl_channel, int(setpnt * step)) # Set brake to desired value
        print('Brake set to', setpnt, 'V')

def brakeOff(test, channelID):
    '''
    power brake off gradually to avoid cogging
    '''
    setpnt = test.convertSig()
    test.cntrl_channel = test_channels[channelID]['cntrl']
    for i in range(1, 6):
        dac.write_dac(test.cntrl_channel, int(step*setpnt*(5-i)/5))
        print(setpnt*(5-i)/5) # debugging
        time.sleep(2)
    power_down(channelID)
    print('brake ', channelID, 'powered off')

def torqueMeasurement(input):
    # Collect 10 data point readings across 1 second
    setData = []
    for i in range (0, 10):
        raw_channels = ads.read_oneshot(input)
        time.sleep(0.1)
        setData.append(raw_channels)
    # Remove max and min values
    setData.remove(max(setData)) 
    setData.remove(min(setData))
    rawVal = float(sum(setData)/len(setData)) # Average everything else

    voltage = float(rawVal*astep) # Convert raw value to voltage
    print('voltage reading: ', voltage) # for troubleshooting/calibration
    torque = torqueConvert(voltage) # Convert voltage value to torque value
    print('torque reading:', torque)
    return torque

def torqueConvert(volt):
    torqueVal = (volt - 2.5)*6000/2.5 #convert reading to torque value in in-lbs
    return(torqueVal)
def restCalc(length, dCycle):
    '''
    Calculate a new cycle time using the length of the last half cycle, and the duty cycle setting of the test 
    '''
    rest = float(length / (float(dCycle)/100))
    return rest

def switchCheck(test, testIndex):
    '''
    Read the state of the actuator limit switch inputs
    If they changed, do some stuff, if they haven't changed, then do nothing '''

    if test.active == True:
        if (test.pv < test.target): # Check to see if the current cycle count is less than the target
            open_switch = test_channels[testIndex]['FK_On']
            closed_switch = test_channels[testIndex]['FK_Off']
            open_state = GPIO.input(open_switch)
            closed_state = GPIO.input(closed_switch)
            open_last_state = test.open_last_state # Store the last FK_On switch state in a temp variable
            closed_last_state = test.closed_last_state # Store the last FK_Off switch state in temp variable
            
            if (open_last_state == LOW) & (open_state == HIGH) & (closed_state == HIGH): # Check if changed from fully open position to closing (moving)
                print('closed state: ', closed_state) # debugging
                print('open state: ', open_state) # debugging
                print('closed last state: ', closed_last_state) # debugging
                print('open last state: ', open_last_state) # debugging
                test.open_last_state = HIGH # Reset the "open last state" of the switch
                length = time.time() - test.cycle_start # Calculate the length of the last duty cycle

                if (length > (test.duty_cycle*.49)):
                    test.cycle_start = time.time() # update cycle start time
                    test.pv+= 1 # Increment the pv counter if the switch changed
                    print('test.pv: ', test.pv)
                    print("Switch {} confirmed. Actuator is closing.".format(test.name))

                    # collect "cycle_points" amount of points in cycle
                    for y in range (test.cycle_points):
                        while True:
                            # wait 1/3 of cycle time or 1/cyclepoints
                            if (time.time() - test.cycle_start) > (((y)/test.cycle_points)*test.cycle_time):
                                tor = torqueMeasurement(test_channels[testIndex]['torq'])
                                print('torque in switchcheck:', tor) # debugging
                                test.torque.append(tor) # store torque reading measurement
                                # store other values
                                test.time.append(time.time())
                                break
                else:
                    test.bounces = test.bounces + 1
                    print("Switch {} bounced. Bounce count: {}.".format(testIndex, test.bounces))

            elif (closed_last_state == LOW) & (closed_state == HIGH) & (open_state == HIGH): # Check if changed from fully closed position to opening (moving)
                print('closed state: ', closed_state) # debugging
                print('open state: ', open_state) # debugging
                print('closed last state: ', closed_last_state) # debugging
                print('open last state: ', open_last_state) # debugging
                test.closed_last_state = HIGH # Reset the "closed last state" of the switch
                length = time.time() - test.cycle_start # Calculate the length of the last duty cycle

                if (length > (test.duty_cycle*.49)):
                    test.cycle_start = time.time() # Update cycle start time
                    test.pv+= 1 # Increment the pv counter if the switch changed
                    print('test.pv: ', test.pv)
                    print("Switch {} confirmed. Actuator is opening.".format(test.name))

                    # collect "cycle_points" amount of points in cycle
                    for y in range (test.cycle_points):
                        # wait 1/3 of cycle time or 1/cyclepoints
                        while True:
                            if (time.time() - test.cycle_start) > (((y)/test.cycle_points)*test.cycle_time):
                                tor = torqueMeasurement(test_channels[testIndex]['torq'])
                                print('torque in switchcheck: ', tor) # debugging
                                test.torque.append(tor) # store torque reading measurement
                                # store other values
                                test.time.append(time.time())
                                break
                else:
                    test.bounces = test.bounces + 1
                    print("Switch {} bounced. Bounce count: {}.".format(testIndex, test.bounces))

            elif (open_last_state == HIGH) & (open_state == LOW) & (closed_state == HIGH): # Check to see if recently in fully open position
                print('closed state: ', closed_state) # debugging
                print('open state: ', open_state) # debugging
                print('closed last state: ', closed_last_state) # debugging
                print('open last state: ', open_last_state) # debugging
                print("Switch {} changed. Actuator is in fully open position.".format(testIndex))
                test.open_last_state = LOW # Update last switch state
                test.cycle_time = time.time() - test.cycle_time # Update cycle_time
                print('test.cycle_time updated to: ', test.cycle_time)

            elif (closed_last_state == HIGH) & (closed_state == LOW) & (open_state == HIGH): # Check to see if recently in fully closed position
                print('closed state: ', closed_state) # debugging
                print('open state: ', open_state) # debugging
                print('closed last state: ', closed_last_state) # debugging
                print('open last state: ', open_last_state) # debugging
                print("Switch {} changed. Actuator is in fully closed position.".format(testIndex))
                test.closed_last_state = LOW # Update last switch state
                test.cycle_time = time.time() - test.cycle_time # Update cycle_time
                print('test.cycle_time updated to: ', test.cycle_time)print('test.cycle_time updated to: ', test.cycle_time)

            else:
                pass
        else:
            test.active = False
    else:
        pass

def onOff_measurement(inputs):

    # Read the input voltages from the current and brake control inputs on the ADC. 
    # Voltages are converted from raw integer inputs using convert functions in this library
    
    raw_channels = ads.read_sequence(inputs)
    cntrl = raw_channels[0]
    curr = raw_channels[1]
    return(cntrl, curr)  

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
        killDeamons()
        raise Warning("You didn't catch all of the cases")

def power_down(testindex):
    print('powering down dac')
    test = tests[testindex]
    dac.power_down(CH_Out[test], MODE_POWER_DOWN_100K)

def killDaemons():
    print('sacrificing IO daemons') # Kill the IO daemon process
    bash = "sudo killall pigpiod" 
    process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()









