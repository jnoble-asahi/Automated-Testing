import os
import time
from  gpiozero import Button 
import pigpio as io 
import sys
import subprocess

bash = "sudo pigpiod" 
process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

ch1 = Button(6, pull_up = True)
ch2 = Button(13, pull_up = True)
ch3 = Button(19, pull_up = True)

inputs = (ch1, ch2, ch3)

def switchCheck(channel):
        state = channel.value
        print(state)


last = time.time()
wait = 3
i = 0
while True:
    if time.time() - last < wait:
        pass
    else:
        for item in inputs:
            print('Channel {} is currently {}, check # {}'.format(item, item.value, i))
            last = time.time()
            i += 1
