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

# Set pin numbers for the relay channels and the limit switch inputs
# Note that the pin numbers here follow the wiringPI scheme, which we've setup for *.phys or the GPIO header locations
# Since the wiringpi module communicates through the GPIO, there shouldn't be a need to initiate the SPI bus connection
wp.wiringPiSetupPhys()
HIGH = onf.HIGH
LOW = onf.LOW

channels = [onf.one.channel[0], onf.two.channel[0], onf.three.channel[0]]

address = an.INPUTS_ADDRESS
posIn = (address[0], address[1])
curIn = (address[2], address[3], address[4])
tempIn = (address[5], address[6], address[7])

CH1_SEQ = (address[5], address[6], address[7], address[2], address[3], address[4])

print('setting IO channels')
for i in range(len(channels)):
    wp.pinMode(channels[i], onf.OUTPUT) # Declare pins to be used as outputs
    wp.digitalWrite(channels[i], HIGH) # Set the output pins HIGH to start the test
    print('Channel ', i, 'set HIGH')
print("Relay Module Set-up")

temp1 = []
temp2 = []
temp3 = []
cur1 = []
cur2 = []
cur3 = []
stamp = []

sampleRate = 30
writeRate = 1800
testTime = 21600
start = time.time()
last = 0
lastWrite = time.time()

while (time.time() - start) < testTime:
    if (time.time() - last) > sampleRate:
<<<<<<< HEAD
        read1 = an.curTempRead(CH1_SEQ)
        temp1 = temp1.append(an.tempConvert(read1[0]))
        temp2 = temp2.append(an.tempConvert(read1[1]))
        temp3 = temp3.append(an.tempConvert(read1[2]))
        cur1 = cur1.append(an.currentConvert(read1[3]))
        cur2 = cur2.append(an.currentConvert(read1[4]))
        cur3 = cur3.append(an.currentConvert(read1[5]))
        print('Temp1 Measurement', an.tempConvert(read1[0]))
        print('Current 1 Measurement', an.currentConvert(read1[4]))
        stamp = stamp.append(time.time())
=======
        read1 = an.do_measurement(CH1_SEQ, 0)
        temp1.append(an.tempConvert(read1[0]))
        temp2.append(an.tempConvert(read1[1]))
        temp3.append(an.tempConvert(read1[2]))
        cur1.append(an.currentConvert(read1[3]))
        cur2.append(an.currentConvert(read1[4]))
        cur3.append(an.currentConvert(read1[5]))
        stamp.append(time.time())
>>>>>>> upstream/master
        last = time.time()
    else:
        time.sleep(2)
    if (time.time() - lastWrite) > writeRate:
        df1 = pd.DataFrame({ 'time' : stamp,
                            'Temp1' : temp1,
                            'Temp2' : temp2,
                            'Temp3' : temp3,
                            'Current1' : cur1,
                            'Current2' : cur2,
                            'Current3' : cur3})
        df1.to_csv('tempTests1.csv', sep = ',')
    else:
        time.sleep(2)

df1 = pd.DataFrame({ 'time' : stamp,
                    'Temp1' : temp1,
                    'Temp2' : temp2,
                    'Temp3' : temp3,
                    'Current1' : cur1,
                    'Current2' : cur2,
                    'Current3' : cur3})
df1.to_csv('tempTests1.csv', sep = ',')

print('sacrificing IO daemons')

bash = "sudo killall pigpiod" 
process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
output, error = process.communicate()


