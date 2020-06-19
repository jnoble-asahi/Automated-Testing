import os
import time
import sys
import math as mt
import numpy as np
import subprocess

import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BOARD)
GPIO.setup(31, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(33, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(35, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(37, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    print ('input 6:', GPIO.input(31))
    print ('input 13:', GPIO.input(33))
    print ('input 19:', GPIO.input(35))
    print ('input 26:', GPIO.input(37))
    time.sleep(2.5)