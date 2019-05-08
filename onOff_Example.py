############################################
''' This is a rough draft of code required to run the actuation tester prototype
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
import onOffConfigs as onf 

# Test it out by creating a new class instance
testUrl = 'https://tufts.box.com/shared/static/kpsnw7ozeytd04wyge1h2oly5pqbrb3k.csv'
paras = pd.read_csv(testUrl)
paras.head()

one = onf.on_off()
two = onf.on_off()
three = onf.on_off()

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

channels = [one.channel[0], two.channel[0], three.channel[0]]
inputs = [one.inputs[0], two.inputs[0], three.inputs[0]]
cycleTimes = [one.cycleTime[0], two.cycleTime[0], three.cycleTime[0]]
testTime = [one.time[0], two.time[0], three.time[0]]
cycles = [one.no_cycles[0], two.no_cycles[0], three.no_cycles[0]]
duty = [one.duty_cycle[0], two.duty_cycle[0], three.duty_cycle[0]]
torque = [one.torque_req[0], two.torque_req[0], three.torque_req[0]]

# Set pin numbers for the relay channels and the limit switch inputs
# Note that the pin numbers here follow the wiringPI scheme, which we've setup for *.phys or the GPIO header locations
# Since the wiringpi module communicates through the GPIO, there shouldn't be a need to initiate the SPI bus connection
wp.wiringPiSetupPhys()
HIGH = onf.HIGH
LOW = onf.LOW

for i in range(len(channels)):
    wp.pinMode(channels[i], onf.OUTPUT)
    wp.pinMode(inputs[i], onf.INPUT)
    wp.digitalWrite(channels[i], HIGH)
    print('Channel ', i, 'set HIGH')

print("Relay Module Set-up")

print("Actuator Opening")
time.sleep(0.1)
cycleStart = [time.time(), time.time(), time.time()]
pv = [0, 0, 0]
cnt = [0, 0, 0]
ls = [HIGH, HIGH, HIGH]
sw = [HIGH, HIGH, HIGH]

while 1000 > pv[0]: # Flagging this to change later, should be changed to while True or another statement
    currentTime = time.time()
    for pin in range(len(inputs)):
        state = wp.digitalRead(inputs[pin])
        if sw[pin] == HIGH & state == LOW:
            time.sleep(0.125)
            state = wp.digitalRead(inputs[pin])
            if state == LOW:
                print('Switch Confirmed')
                pv[pin] += 1
                sw[pin] = LOW
                length = time.time() - cycleStart[pin]
                if pv[pin] > 2:
                    cycleTimes[pin] = onf.restCalc(length, duty[pin])
                    print('Setting cycle time as: ', cycleTimes[pin])
                else:
                    pass
            else:
                pass
        if sw[pin] == LOW & state == HIGH:
            time.sleep(0.125)
            state = wp.digitalRead(pin)
            if state == HIGH:
                print('Switch position changed')
                sw[pin] = HIGH
            else:
                pass
        else:
            Warning('Error with switch check function, did you catch all the possible cases?')        
    for pin in range(len(channels)):
        if currentTime - cycleStart[pin] > cycleTimes[pin]:
            if ls[pin] == HIGH:
                wp.digitalWrite(channels[pin], onf.LOW)
                ls[pin] = LOW
                cycleStart[pin] = time.time()
                print('Actuator Closing')
                time.sleep(0.1)
            elif ls[pin] == LOW:
                wp.digitalWrite(channels[pin], onf.HIGH)
                ls[pin] = HIGH
                cycleStart[pin] = time.time()
                cnt[pin] += 1
                print('Actuator Opening')
                time.sleep(0.1)
            else:
                Warning('Open the pod bay doors Hal')
                ls[pin] = HIGH
                cycleStart[pin] = time.time()
                time.sleep(0.1)
print("except")