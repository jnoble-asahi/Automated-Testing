############################################
''' This is a rough draft of code required to run the actuation tester prototype
The script loads two other programs - ADC_Script and DAC_Script
The project requires a large number of dependencies from other libraries
Full details on dependencies and set-up instructions on Github here: exampleURL.com
Pin callouts in this program refer to the wiringPI addresses and not GPIO pin numbers
This script written by Chris May - pezLyfe on github
######## '''
import os
import time
import os
import wiringpi as wp 
import sys
import math as mt
import numpy as np
import pandas as pd 

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
        self.length = []
        self.inputs = []
        self.torque_req = []
        self.in_voltage = []
    
    def setCycleTime(self):
        '''
        Raise a text prompt that requests the test channel. If the number is outside the working range, throw an exception
        Otherwise, set the test length and then cast it as a tuple to make it immutable
        '''
        temp = input('Enter the half cycle time: ')
        if temp not in range(1, 60, 1):
            Warning('Cycle times must be whole number between 1 and 60')
        else:
            self.cycleTime.append(temp)
            list(self.cycleTime)
            print('Test cycle time created')

    def setChannel(self):
        '''
        Raise a text prompt that requests the test channel. If the number is outside the working range, throw an exception
        Otherwise, set the test length and then cast it as a tuple to make it immutable
        '''
        temp = input('Enter the desired test channel: ')
        if temp not in range(1, 4, 1):
            Warning('Test channel must be iether 1, 2, or 3')
        else:
            self.channel.append(relayChannels[temp])
            self.inputs.append(actInputs[temp])
            tuple(self.channel)
            tuple(self.inputs)
            print('Test channel and input pin fixed ')

    def setTime(self):
        self.time.append(time.time())
        print('Test start time logged')
    
    def setCycles(self):
        '''
        Raise a text prompt that requests the test length. If the number is outside the normal working range, throw an exception
        Otherwise, set the test length and then cast it as a tuple to make it immutable
        '''
        temp = input('Enter the desired number of test cycles: ')
        if temp not in range(1, 1000000, 1):
            raise ValueError('Number of cycles must be a whole number, between 1 and 1,000,000')
        else:
            self.no_cycles.append(int(temp))
            tuple(self.no_cycles)
            print('Test cycles set point created')
    
    def setDuty(self):
        '''
        Raise a text prompt that requests the duty cycle. If the number is outside the normal working range, throw an exception
        Otherwise, set the test length and then cast it as a tuple to make it immutable
        '''
        temp = input('Enter the desired duty cycle, as a number betweeo 1 - 100: ')
        if temp not in range(0, 100, 1):
            raise ValueError('Duty cycle must be a whole number between 1 and 100')
        else:
            self.duty_cycle.append(int(temp))
            tuple(self.duty_cycle)
            print('Test duty cycle created')

    def setTorque(self):
        '''
        Raise a text prompt for the user to input hte torque rating of the actuator. This portion is only logged right now, but will be
        important for future use when it's combined with an electromechanical load
        '''
        temp = input('Enter the torque rating of the actuator, in in-lbs: ')
        if temp not in range(20, 5000, 1):
            raise ValueError('Test torques must be a whole number between 20 - 5000')
        else:
            self.torque_req.append(int(temp))
            tuple(self.torque_req)
            print('Torque range created')

    def setVoltage(self):
        '''
        Raise a text prompt for the user to input the operating voltage of the actuator. This portion is only logged right now, but will
        be important later when we abstract away setting operating voltages through terminal connections
        '''
        temp = input('Enter the working voltage of the actuator. Options are: 120VAC, 220VAC, 24VDC, 12VDC: ')
        if temp not in volts:
            raise ValueError('Voltage not in the correct range, please enter one of the following: 120VAC, 220VAC, 24VDC, 12VDC')
        else:
            self.in_voltage.append(str(temp))
            tuple(self.in_voltage)
            print('Working voltage fixed')

# Test it out by creating a new class instance

one = on_off()
two = on_off()
three = on_off()

one.setChannel()
print('Test set on channel ', one.channel[0])
print('Test input set on pin ', one.inputs[0])

two.setChannel()
print('Test set on channel ', two.channel[0])
print('Test input set on pin ', two.inputs[0])

three.setChannel()
print('Test set on channel ', three.channel[0])
print('Test input set on pin ', three.inputs[0])

channels = [one.channel[0], two.channel[0], three.channel[0]]
inputs = [one.inputs[0], two.inputs[0], three.inputs[0]]

one.setCycleTime()
print('Test cycle time set as ', one.cycleTime[0])

two.setCycleTime()
print('Test cycle time set as ', two.cycleTime[0])

three.setCycleTime()
print('Test cycle time set as ', three.cycleTime[0])

cycleTimes = [one.cycleTime[0], two.cycleTime[0], three.cycleTime[0]]

one.setTime()
print('Test started at: ', one.time[0], ' epoch time')

two.setTime()
print('Test started at: ', two.time[0], ' epoch time')

three.setTime()
print('Test started at: ', three.time[0], ' epoch time')

testTime = [one.time[0], two.time[0], three.time[0]]

one.setCycles()
print('Test target cycles set at: ', one.no_cycles[0], ' cycles')

two.setCycles()
print('Test target cycles set at: ', two.no_cycles[0], ' cycles')

three.setCycles()
print('Test target cycles set at: ', three.no_cycles[0], ' cycles')

cycles = [one.no_cycles[0], two.no_cycles[0], three.no_cycles[0]]

one.setDuty()
print('Duty cycle set for: ', one.duty_cycle[0], '%')

two.setDuty()
print('Duty cycle set for: ', two.duty_cycle[0], '%')

three.setDuty()
print('Duty cycle set for: ', three.duty_cycle[0], '%')

duty = [one.duty_cycle[0], two.duty_cycle[0], three.duty_cycle[0]]

one.setTorque()
print('Torque range set for: ', one.torque_req[0], ' in-lbs')

two.setTorque()
print('Torque range set for: ', two.torque_req[0], ' in-lbs')

three.setTorque()
print('Torque range set for: ', three.torque_req[0], ' in-lbs')

torque = [one.torque_req[0], two.torque_req[0], three.torque_req[0]]

# Set pin numbers for the relay channels and the limit switch inputs
# Note that the pin numbers here follow the wiringPI scheme, which we've setup for *.phys or the GPIO header locations
# Since the wiringpi module communicates through the GPIO, there shouldn't be a need to initiate the SPI bus connection
wp.wiringPiSetupPhys()

binary = {'INPUT' : 0,
          'OUTPUT': 1,
          'LOW' : 0,
          'HIGH' : 1}

OUTPUT = binary['OUTPUT']
INPUT = binary['INPUT']
LOW = binary['LOW']
HIGH = binary['HIGH']

wp.pinMode(channels[0], OUTPUT)
wp.pinMode(channels[1], OUTPUT)
wp.pinMode(channels[2], OUTPUT)

wp.pinMode(inputs[0], INPUT)
wp.pinMode(inputs[1], INPUT)
wp.pinMode(inputs[2], INPUT)

print("Relay Module Set-up")
        
# Start the test by turning on all relays
wp.digitalWrite(channels[0], HIGH)
wp.digitalWrite(channels[1], HIGH)
wp.digitalWrite(channels[2], HIGH)

pos = ['HIGH', 'HIGH', 'HIGH']
print("Actuator Opening")
time.sleep(0.1)
cycleStart = [time.time(), time.time(), time.time()]
pv = [0, 0, 0]
cnt = [0, 0, 0]
ls = ['HIGH', 'HIGH', 'HIGH']
names = []

def restCalc(length, dCycle):
    '''
    Calculate the rest time between cycles. First calculate the length of the last cycle then divide by the duty cycle.
    Divide that result by 2, since we want the rest time for each half cycle and we're only tracking the full cycle positively. 
    '''
    rest = (length / dCycle) / 2
    return(rest)

def switchCheck(ls, pin):
    '''
    Check the state of the input and compare it against the previous state
    If the state has changed, debounce it and then do something
    '''
    state = wp.digitalRead(pin)
    if ls == HIGH & state == LOW:
        time.sleep(0.125)
        if state == LOW:
            return('Confirmed')
        else:
            return('Same')
    if ls == LOW & state == HIGH:
        time.sleep(0.125)
        if state == HIGH:
            return('Changed')
        else:
            return('Same')
    else:
        Warning('Error with switch check function, did you catch all the possible cases?')
        return('Same')

while 1000 > pv[0]: # Flagging this to change later, should be changed to while True or another statement
    currentTime = time.time()
    for i in range(len(inputs)):
        print(i)
        temp1 = ls[i]
        temp2 = inputs[i]
        status = switchCheck(temp1, temp2) # Make sure the iterator works here, may have to change to i
        if status == 'Confirmed':
            pv[i] += 1
            ls[i] = 'LOW'
            length = time.time() - cycleStart[i]
            if pv[i] > 2:
                cycleTimes[i] = restCalc(length, duty[i])
                print('Setting cycle time as: ', cycleTimes[i])
        elif status == 'Changed':
            ls[i] = 'HIGH'
        elif status == 'Same':
            pass
        else:
            Warning('Error with switchCheck function')
    for pin in range(len(channels)):
        if currentTime - cycleStart[pin] > cycleTimes[pin]:
            if ls[pin] == 'HIGH':
                wp.digitalWrite(channels[pin], LOW)
                ls[pin] = 'LOW'
                cycleStart[pin] = time.time()
                print('Actuator Closing')
                time.sleep(0.1)
            elif ls[pin] == 'LOW':
                wp.digitalWrite(channels[pin], HIGH)
                ls[pin] = 'HIGH'
                cycleStart[pin] = time.time()
                cnt[pin] += 1
                print('Actuator Opening')
                time.sleep(0.1)
            else:
                Warning('Open the pod bay doors Hal')
                ls[pin] = 'HIGH'
                cycleStart[pin] = time.time()
                time.sleep(0.1)
print("except")
GPIO.cleanup()