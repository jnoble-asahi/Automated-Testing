import os
import time
import sys
import math as mt
import numpy as np
import subprocess

import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    print ('input 13:', GPIO.input(13))
    print ('input 19:', GPIO.input(19))
    time.sleep(2)