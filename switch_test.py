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

binary = {'INPUT' : 0,
          'OUTPUT': 1,
          'LOW' : 0,
          'HIGH' : 1}

ch1 = 31
ch2 = 33
ch3 = 35

inputs = (ch1, ch2, ch3)

for i, value in enumerate(inputs):
    wp.pinMode(inputs[i], binary['INPUT']) # Declare the pins connected to limit switches as digital inputs
    #wp.pullUpDnControl(inputs[i], 2) # Set the input pins for pull up control
    print("Pin {} set up for pull up control".format(inputs[i]))


def switchCheck(channel):
        state = wp.digitalRead(channel)
        print(state)


last = time.time()
wait = 3
while True:
    if time.time() - last < wait:
        pass
    else:
        switchCheck(35)
        last = time.time()
        #for i, value in enumerate(inputs):
        #    switchCheck(inputs[i])
            
    


