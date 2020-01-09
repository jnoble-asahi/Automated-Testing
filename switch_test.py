import os
import time
import wiringpi as wp
import pigpio as io 
import sys
import subprocess

bash = "sudo pigpiod" 
process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

wp.wiringPiSetupPhys()

ch1 = 31
ch2 = 33
ch3 = 35

inputs = (ch1, ch2, ch3)

for item in inputs:
    wp.pinMode(inputs[item], INPUT) # Declare the pins connected to limit switches as digital inputs
    wp.pullUpDnControl(inputs[item], 2) # Set the input pins for pull up control
    print("Pin {} set up for pull up control").format(inputs[item])


def switchCheck(channel):
        state = wp.digitalread(channel)
        print(state)


last = time.time()
wait = 3
while True:
    if time.time() - last < wait:
        pass
    else:
        for item in inputs:
            switchCheck(inputs[item])
            last = time.time()
    


