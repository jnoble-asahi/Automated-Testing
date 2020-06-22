import os
import time
import sys
import math as mt
import numpy as np
import subprocess

import wiringpi as wp

wp.wiringPiSetupPhys()

wp.pullUpDnControl(13, 2)
s = wp.digitalRead(13)
print(s)
time.sleep(3)
state = wp.digitalRead(13)
print(state)

'''import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BOARD)
GPIO.setup(31, GPIO.IN, pull_up_down=GPIO.PUD_UP)
'GPIO.setup(33, GPIO.IN, pull_up_down=GPIO.PUD_UP)'
'GPIO.setup(35, GPIO.IN, pull_up_down=GPIO.PUD_UP)'
'GPIO.setup(37, GPIO.IN, pull_up_down=GPIO.PUD_UP)'
GPIO.setup(33, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(35, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(37, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

for x in range (0, 30):
    print ('input 6:', GPIO.input(31))
    print ('input 13:', GPIO.input(33))
    print ('input 19:', GPIO.input(35))
    print ('input 26:', GPIO.input(37))
    time.sleep(2.5)

GPIO.cleanup()'''