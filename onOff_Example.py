############################################
''' This is a rough draft of code required to run the actuation tester prototype
Full details on dependencies and set-up instructions on Github here: exampleURL.com
Pin callouts in this program refer to the wiringPI addresses and not GPIO pin numbers
This script written by Chris May - pezLyfe on github
######## '''
import os
import time
import wiringpi as wp 
import pigpio as io
import sys
import math as mt
import numpy as np
import pandas as pd 
import onOffConfigs as onf 
import adc_dac_config as an 
import subprocess

# Start the pigpio daemon 
bash = "sudo pigpiod" 
process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

print('configuring test parameters')
channels = [onf.one.channel[0], onf.two.channel[0], onf.three.channel[0]]
inputs = [onf.one.inputs[0], onf.two.inputs[0], onf.three.inputs[0]]
cycleTimes = [onf.one.cycleTime[0], onf.two.cycleTime[0], onf.three.cycleTime[0]]
testTime = [onf.one.time[0], onf.two.time[0], onf.three.time[0]]
cycles = [onf.one.no_cycles[0], onf.two.no_cycles[0], onf.three.no_cycles[0]]
duty = [onf.one.duty_cycle[0], onf.two.duty_cycle[0], onf.three.duty_cycle[0]]
torque = [onf.one.torque_req[0], onf.two.torque_req[0], onf.three.torque_req[0]]

# Set pin numbers for the relay channels and the limit switch inputs
# Note that the pin numbers here follow the wiringPI scheme, which we've setup for *.phys or the GPIO header locations
# Since the wiringpi module communicates through the GPIO, there shouldn't be a need to initiate the SPI bus connection
wp.wiringPiSetupPhys()
HIGH = onf.HIGH
LOW = onf.LOW

print('setting IO channels')
for i in enumerate(channels):
    wp.pinMode(channels[i], onf.OUTPUT) # Declare pins to be used as outputs
    wp.pinMode(inputs[i], onf.INPUT) # Declare pins to be used as inputs
    wp.pullUpDnControl(inputs[i], 2) # Set the input pins for pull up control
    wp.digitalWrite(channels[i], HIGH) # Set the output pins HIGH to start the test
    print('Channel ', i, 'set HIGH')
print("Relay Module Set-up")

# Log times to set a baseline for when to take measurements/cycle the actuators
cycleStart = [time.time(), time.time(), time.time()]
tempTime = [time.time(), time.time(), time.time()]
currTime = [time.time(), time.time(), time.time()]
last_print = time.time()
print_rate = 900

# Set initial states for cycle pv, shot counts, relay state, and switch position
pv = [0, 0, 0]
cnt = [0, 0, 0]
ls = [HIGH, HIGH, HIGH]
sw = [HIGH, HIGH, HIGH]

# Create tuples for the ADC addresses for current, temperature, and position inputs
address = an.INPUTS_ADDRESS
posIn = (address[0], address[1])
curIn = (address[2], address[3], address[4])
tempIn = (address[5], address[6], address[7])

# Create empty dataframes for the test channels. Since the tests aren't necessarily synchronous, the datalogging should be kept separate
test1 = pd.DataFrame()
test2 = pd.DataFrame()
test3 = pd.DataFrame()

while 1000 > pv[0]: # Flagging this to change later, should be changed to while True or another statement
    currentTime = time.time()
    for pin in range(len(inputs)):
        state = wp.digitalRead(inputs[pin])
        if ((sw[pin] == HIGH) & (state == LOW)):
            print('Switch ', pin, ' confirmed')
            pv[pin] += 1
            sw[pin] = LOW
            length = time.time() - cycleStart[pin]
            if pv[pin] > 2:
                cycleTimes[pin] = onf.restCalc(length, duty[pin])
                print('Setting cycle time as: ', cycleTimes[pin])
            else:
                pass
        elif ((sw[pin] == LOW) & (state == HIGH)):
            print('Switch ', pin, ' changed')
            sw[pin] = HIGH
        else:
            Warning('Error with switch check, did you catch all the possible cases?')        
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
                time.sleep(0.25)
                t = an.tempMeasurement(tempIn[i])
                c = an.currentMeasurement(curIn[i])
                data_list = list([currentTime, t, c, pv[i], cnt[i]])
                df = pd.DataFrame(data = [data_list], columns = ['time', 'temp', 'current', 'present_value', 'shot_count'])
                if pin == 0:
                    test1 = test1.append(df, ignore_index = True)
                elif pin == 1:
                    test2 = test2.append(df, ignore_index = True)
                elif pin == 2:
                    test3 = test3.append(df, ignore_index = True)
                else:
                    Warning('Test index out of range, check setup')
            else:
                Warning('Open the pod bay doors Hal')
                ls[pin] = HIGH
                cycleStart[pin] = time.time()
                time.sleep(0.1)
    if currentTime - last_print > print_rate:
        test1.to_csv("test1_logs.csv")
        test2.to_csv("test2_logs.csv")
        test3.to_csv("test3_logs.csv")
        last_print = time.time()

test1.to_csv("test1_logs.csv")
test2.to_csv("test2_logs.csv")
test3.to_csv("test3_logs.csv")

print('sacrificing IO daemons')

bash = "sudo killall pigpiod" 
process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

print("except")