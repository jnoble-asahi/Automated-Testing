import os
import time
from  gpiozero import Button 
import pigpio as io 
import sys
import subprocess

bash = "sudo pigpiod" 
process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

ch1 = Button(6)
ch2 = Button(13)
ch3 = Button(19)

inputs = (ch1, ch2, ch3)

def switchCheck(channel):
        state = channel.value
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

i = 0
#change