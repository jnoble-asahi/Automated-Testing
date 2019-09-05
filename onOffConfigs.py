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
           'temp' : INPUTS_ADDRESS[5]}

CH2_Loc = {'pos' : INPUTS_ADDRESS[1],
           'cur' : INPUTS_ADDRESS[3],
           'temp' : INPUTS_ADDRESS[6]}

CH3_Loc = {'pos' : INPUTS_ADDRESS[0],
           'cur' : INPUTS_ADDRESS[4],
           'temp' : INPUTS_ADDRESS[7]}

CH1_SEQUENCE = (CH1_Loc['pos'], CH1_Loc['cur'], CH1_Loc['temp']) #Position, Current, Temperature channels

CH2_SEQUENCE =  (CH2_Loc['pos'], CH2_Loc['cur'], CH2_Loc['temp']) #Position, Current, Temperature channels

CH3_SEQUENCE =  (CH3_Loc['pos'], CH3_Loc['cur'], CH3_Loc['temp']) #Position, Current, Temperature channels

inputSequence = {1 : CH1_SEQUENCE,
                 2 : CH2_SEQUENCE,
                 3 : CH3_SEQUENCE} 

tests = ('1', '2', '3')

binary = {'INPUT' : 0,
          'OUTPUT': 1,
          'LOW' : 0,
          'HIGH' : 1}

OUTPUT = binary['OUTPUT']
INPUT = binary['INPUT']
LOW = binary['LOW']
HIGH = binary['HIGH']

relayChannels = {1 : 37,
                 2 : 38,
                 3 : 40}

chans = list(relayChannels.keys())

actInputs = {1 : 31,
             2 : 33,
             3 : 35}

voltages = {'120VAC': 120,
            '220VAC': 220,
            '24VDC' : 24,
            '12VDC' : 12}

volts = list(voltages.keys())

Relay_Ch1 = 37
Relay_Ch2 = 38
Relay_Ch3 = 40

# Define the on/off test as a class
    def createTest(self, channel, cycleTime, cycles, dutyCycle, torque):
        self.setChannel(channel)
        self.setCycleTime(cycleTime)
        self.setCycles(cycles)
        self.setTime()
        self.setDuty(dutyCycle)
        self.setTorque(torque)
    
        prompt = raw_input("Activate test on channel {}? (Y/N)".format(self.name))
        i = 0
        while i < 1:
            if prompt == "Y":
                self.active = True
                wp.pinMode(self.channel, OUTPUT) # Declare the pins connected to relays as digital outputs
                wp.pinMode(self.input, INPUT) # Decalre the pins connected to limit switches as digital inputs
                wp.pullUpDnControl(self.input, 2) # Set the input pins for pull up control
                wp.digitalWrite(self.channel, HIGH) # Write HIGH to the relay pins to start the test
                print("Channel {} set HIGH".format(self.name))
                i += 1 # Increment the loop if reading the prompt was successful
            elif prompt == "N":
                self.active = False # De-activate the test channel if it's not being used
                print("Channel {} set inactive".format(self.name))
                i += 1
            else:
                print("Input must be either Y or N") # Don't increment the loop if a bad input was entered

    def setChannel(self, chanNumber):
        '''
        Read the channel from the test parameters sheet and check that it's in the proper range. If not raise a warning. Cast it as 
        a tuple to make it immutable
        '''
        if chanNumber not in range(1, 4, 1):
            raise ValueError('Test channel must be either 1, 2, or 3')
        else:
            self.channel = (relayChannels[chanNumber])
            self.name = chanNumber
            self.input = (actInputs[chanNumber])
            self.inputSequence = inputSequence[chanNumber]
            print('Test channel and input pin fixed ')

def restCalc(length, dCycle):
    '''
    Calculate a new cycle time using the length of the last half cycle, and the duty cycle setting of the test 
    '''
    rest = float(length / (float(dCycle)/100))
    return(rest)

def switchCheck(testChannel, switchInput):
    '''
    Read the state of the actuator limit switch input
    If it's changed, do some stuff, if it hasn't changed, then do nothing
    '''
    state = wp.digitalRead(switchInput) # Reads the current switch state
    lastState = testChannel.lastState # Store the last switch state in a temp variable
    if (lastState == HIGH) & (state == LOW): # Check if the switch changed from HIGH to LOW 
        testChannel.lastState = LOW #Reset the "last state" of the switch
        length = time.time() - testChannel.cycleStart # Calculate the length of the last cycle
        testChannel.cycleTimeNow = float("{0:.2f}".format(length)) # Store the last cycle time for use in datalogging
        if (length > (testChannel.cycleTime*.25)):
            testChannel.pv = testChannel.pv + 1 # Increment the pv counter if the switch changed
            print("Switch {} confirmed".format(testChannel.name))
        else:
            testChannel.bounces = testChannel.bounces + 1
            print("Switch {} bounced".format(testChannel.name))
        '''
        Reserved block to later add duty cycle calc functions
        '''
    elif (lastState == LOW) & (state == HIGH): 
        print("Switch {} changed".format(testChannel.name))
        testChannel.lastState = 1
    else:
        pass

def cycleCheck(testChannel):
    '''
    Run a series of checks against the current time, the relay states, and actuator information
    Do something based on the results of those checks

    Sensor measurments are taken on the close -> open cycle since that's the point where actuator loads are the highest
    '''
    if testChannel.active == True:
        if (testChannel.pv < testChannel.no_cycles): # Check to see if the current cycle count is less than the target
            if (time.time() - testChannel.cycleStart) > (testChannel.cycleTime): # Check to see if the current cycle has gone past the cycle time
                if testChannel.chanState == HIGH: # If both are yes, change the relay state, and update cycle parameters
                    wp.digitalWrite(testChannel.channel, LOW)
                    testChannel.chanState = LOW
                    testChannel.cycleStart = time.time()
                    print("actuator {} closing".format(testChannel.name))
                    time.sleep(0.1)
                elif testChannel.chanState == LOW: #If the actuator recently closed, change the relay state, then take some measurements
                    wp.digitalWrite(testChannel.channel, HIGH) 
                    testChannel.chanState = HIGH
                    testChannel.cycleStart = time.time()
                    testChannel.shotCount = testChannel.shotCount + 1
                    print("Actuator {} opening".format(testChannel.name))
                    x = an.onOff_measurement(testChannel.inputSequence)
                    testChannel.currents.append(x[0])
                    testChannel.temps.append(x[1])
                    testChannel.time.append(time.time())
                    testChannel.cycleTrack.append(testChannel.cycleTimeNow)
                    testChannel.cycleCounts.append(testChannel.pv)
                    testChannel.cycleBounces.append(testChannel.bounces)
                    testChannel.shots.append(testChannel.shotCount)
                else:
                    print("Something's done messed up") # If the switch states don't match the top two conditions, somehow it went wrong
                    testChannel.chanState = LOW
                    testChannel.cycleStart = time.time()
                    time.sleep(0.1)
            else:
                pass
        else:
            testChannel.active = False

def logCheck(testChannel):
    if testChannel.active == True:
        if (time.time() - testChannel.lastLog) > (testChannel.print_rate):
            logData(testChannel)
            testChannel.lastLog = time.time()
        else:
            pass

def logData(testChannel):
    df = pd.DataFrame({
    'Time' : testChannel.time,
    'Cycle' : testChannel.cycleCounts,
    'Cycle_Times' : testChannel.cycleTrack,
    'Temps' : testChannel.temps,
    'Current' : testChannel.currents,
    'Bounces' : testChannel.cycleBounces})
    df.to_csv("onOffAct{}.csv".format(testChannel.name), sep = ',')
    








