import os
import time
import sys
import math as mt
import numpy as np
import wiringpi as wp
import pandas as pd
import subprocess

binary = {'INPUT' : 0,
          'OUTPUT': 1,
          'LOW' : 0,
          'HIGH' : 1}

OUTPUT = binary['OUTPUT']
INPUT = binary['INPUT']
LOW = binary['LOW']
HIGH = binary['HIGH']

relayChannels = {1: 37,
                 2: 38,
                 3: 40}

chans = list(relayChannels.keys())

actInputs = {1 : 31,
             2: 33,
             3: 35}

voltages = {'120VAC': 120,
            '220VAC': 220,
            '24VDC' : 24,
            '12VDC' : 12}

volts = list(voltages.keys())

Relay_Ch1 = 37
Relay_Ch2 = 38
Relay_Ch3 = 40
ch1_in = 31

# Define the on/off test as a class
class on_off:
    '''
    A class used for on/off actuator tests. Tests parameters are fed line by line through text prompts in the command line
    '''
    def __init__(self):
        self.time = []
        self.cycleTime = []
        self.no_cycles = []
        self.channel = []
        self.duty_cycle = []
        self.inputs = []
        self.torque_req = []
        self.in_voltage = []
    
    def setCycleTime(self, cycleTime):
        '''
        Read the cycleTime from the test parameters sheet and check that it's in the proper range. If not raise a warning. Cast it as 
        a list for security.
        '''
        if cycleTime not in range(1, 100, 1):
            raise ValueError('Cycle times must be whole number between 1 and 60')
        else:
            self.cycleTime.append(cycleTime)
            list(self.cycleTime)
            print('Test cycle time created')

    def setChannel(self, chanNumber):
        '''
        Read the channel from the test parameters sheet and check that it's in the proper range. If not raise a warning. Cast it as 
        a tuple to make it immutable
        '''
        if chanNumber not in range(1, 4, 1):
            raise ValueError('Test channel must be either 1, 2, or 3')
        else:
            self.channel.append(relayChannels[chanNumber])
            self.inputs.append(actInputs[chanNumber])
            tuple(self.channel)
            tuple(self.inputs)
            print('Test channel and input pin fixed ')

    def setTime(self):
        self.time.append(time.time())
        print('Test start time logged')
    
    def setCycles(self, cycleTarget):
        '''
        Read the cycle target from the test parameters sheet and check that it's in the proper range. If not raise a warning. Cast it as 
        a tuple to make it immutable
        '''
        if cycleTarget not in range(1, 1000000, 1):
            raise ValueError('Number of cycles must be a whole number, between 1 and 1,000,000')
        else:
            self.no_cycles.append(int(cycleTarget))
            tuple(self.no_cycles)
            print('Test cycles set point created')
    
    def setDuty(self, dutyCycle):
        '''
        Read the duty cycle from the test parameters sheet and check that it's in the proper range. If not raise a warning. Cast it as 
        a tuple to make it immutable
        '''
        if dutyCycle not in range(0, 100, 1):
            raise ValueError('Duty cycle must be a whole number between 1 and 100')
        else:
            self.duty_cycle.append(int(dutyCycle))
            tuple(self.duty_cycle)
            print('Test duty cycle created')

    def setTorque(self, torqueRating):
        '''
        Read the cycle target from the test parameters sheet and check that it's in the proper range. If not raise a warning. Cast it as 
        a tuple to make it immutable. This isn't used right now, but will be important when we tie the test center in with an electro-mechanical
        load
        '''
        if torqueRating not in range(20, 5000, 1):
            raise ValueError('Test torques must be a whole number between 20 - 5000')
        else:
            self.torque_req.append(int(torqueRating))
            tuple(self.torque_req)
            print('Torque range created')

    def setVoltage(self, voltageInput):
        '''
        Read the input voltage from the test paramters sheet. This portion is only logged right now, but will
        be important later when we abstract away setting operating voltages through terminal connections
        '''
        if voltageInput not in volts:
            raise ValueError('Voltage not in the correct range, please enter one of the following: 120VAC, 220VAC, 24VDC, 12VDC')
        else:
            self.in_voltage.append(str(voltageInput))
            tuple(self.in_voltage)
            print('Working voltage fixed')

def restCalc(length, dCycle):
    '''
    Calculate a new cycle time using the length of the last half cycle, and the duty cycle setting of the test 
    '''
    rest = float(length / (float(dCycle)/100))
    return(rest)

def switchCheck(ls, pin):
    '''
    Check the state of the input and compare it against the previous state
    If the state has changed, debounce it and then do something
    '''
    state = wp.digitalRead(pin)
    status = 0
    if ((ls == 1) & (state == 0)):
        status = 1
    elif ((ls == 0) & (state == 1)):
        status = 2
    elif ((ls == 1) & (state == 1)):
        status = 3
    elif ((ls == 0) & (state == LOW)):
        status = 3
    else:
        Warning('Error with switch check, did you catch all the possible cases?')
    return(status)

print('collecting test parameters from THE CLOUD')
# Set test parameters from a .csv file shared in the cloud
testUrl = 'https://tufts.box.com/shared/static/kpsnw7ozeytd04wyge1h2oly5pqbrb3k.csv'
paras = pd.read_csv(testUrl)
paras.head()

one = on_off()
two = on_off()
three = on_off()

one.setChannel(paras['channel'][0])
two.setChannel(paras['channel'][1])
three.setChannel(paras['channel'][2])

one.setCycleTime(paras['cycle time'][0])
two.setCycleTime(paras['cycle time'][1])
three.setCycleTime(paras['cycle time'][2])

one.setCycles(paras['target'][0])
two.setCycles(paras['target'][1])
three.setCycles(paras['target'][2])

one.setTime()
two.setTime()
three.setTime()

one.setDuty(paras['duty cycle'][0])
two.setDuty(paras['duty cycle'][1])
three.setDuty(paras['duty cycle'][2])

one.setTorque(paras['duty cycle'][0])
two.setTorque(paras['duty cycle'][1])
three.setTorque(paras['duty cycle'][2])