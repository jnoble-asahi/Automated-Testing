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

relayChannels = {'Ch1' : 37,
                 'Ch2' : 38,
                 'Ch3' : 40}

chans = list(relayChannels.keys())

actInputs = {'Ch1' : 31,
             'Ch2' : 33,
             'Ch3' : 35}

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
    Define a class used only for on/off actuator tests. When the test is initiated, require the test channel to be specified
    '''
    def __init__(self, channel):
        if channel not in chans:
             raise ValueError('Test channels can only be specified as Ch1, Ch2, or Ch3')
        self.time = []
        self.no_cycles = []
        self.channel = [relayChannels[channel]]
        self.duty_cycle = []
        self.length = []
        self.inputs = [actInputs[channel]]
        self.torque_req = []
        self.in_voltage = []

    def setTime(self):
        self.time.append(time.time())
        print('Test start time logged')
    
    def setCycles(self):
        '''
        Raise a text prompt that requests the test length. If the number is outside the normal working range, throw an exception
        Otherwise, set the test length and then cast it as a tuple to make it immutable
        '''
        temp = input('Enter the desired number of test cycles')
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
        temp = input('Enter the desired duty cycle, as a number betweeo 1 - 100')
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
        temp = input('Enter the torque rating of the actuator, in in-lbs')
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
        temp = input('Enter the working voltage of the actuator. Options are: ' + volts)
        if temp not in volts:
            raise ValueError('Voltage not in the correct range, please enter one of the following, ' + volts)
        else:
            self.in_voltage.append(temp)
            tuple(self.in_voltage)
            print('Working voltage fixed')

# Test it out by creating a new class instance

one = on_off('Ch1')
one.setTime()
one.setCycles()
one.setDuty()
one.setTorque()
one.setVoltage()

print('Relay channel: ', chans)
print('Test started at: ', one.setTime)
print('Test target cycles set at: ', one.setTime)
print('Duty cycle set for: ', one.setCycles)
print('Torque range set for: ', one.setTorque)
print('Voltage set for: ', one.setVoltage)

# Set pin numbers for the relay channels and the limit switch inputs
# Note that the pin numbers here follow the wiringPI scheme, which we've setup for *.phys or the GPIO header locations
# Since the wiringpi module communicates through the GPIO, there shouldn't be a need to initiate the SPI bus connection
wp.wiringPiSetupPhys()

INPUT = 0
OUTPUT = 1
LOW = 0
HIGH = 1

wp.pinMode(Relay_Ch1, OUTPUT)
wp.pinMode(Relay_Ch2, OUTPUT)
wp.pinMode(Relay_Ch3, OUTPUT)

wp.pinMode(ch1_in, INPUT)
print("Relay Module Set-up")

actIn = ch1_in
actOut = Relay_Ch1
actTime = 10/0.75
        
# Start the test by turning on the relay
wp.digitalWrite(actOut, HIGH)
pos = 'HIGH'
print("Actuator Opening")
time.sleep(0.1)
cycleStart = time.time()
test1 = 0

# GPIO inputs are low active (we're tying inputs to GND), so a low input to the GPIO should read as a switch confirmation

while 1000 > test1:
    currentTime = time.time()
    if currentTime - cycleStart > actTime:
        if pos == 'HIGH':
            wp.digitalWrite(actOut, LOW)
            pos = 'LOW'
            cycleStart = time.time()
            print('Actuator Closing')
            time.sleep(0.1)
        elif pos == 'LOW':
            wp.digitalWrite(actOut, HIGH)
            pos = 'HIGH'
            cycleStart = time.time()
            print('Actuator Opening')
            time.sleep(0.1)
        else:
            print('Error, what did you do?')
            pos = 'HIGH'
            cycleStart = time.time()
            time.sleep(0.1)
    elif currentTime - cycleStart < actTime:
        switchState = wp.digitalRead(actIn)
        if switchState == LOW:
            print('switch is closed')
            time.sleep(1)
        elif switchState == HIGH:
            print('switch is open')
            time.sleep(1)
        else:
            print("switch unknown, do you know what you're doing?")
            time.sleep(1)
print("except")
GPIO.cleanup()