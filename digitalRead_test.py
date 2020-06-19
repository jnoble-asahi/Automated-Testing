import os
import time
import sys
import math as mt
import numpy as np
import subprocess

import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    print ('input 6:', GPIO.input(6))
    print ('input 19:', GPIO.input(26))
    time.sleep(2)