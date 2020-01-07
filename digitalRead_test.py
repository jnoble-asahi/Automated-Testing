import os
import time
import sys
import math as mt
import numpy as np
import subprocess

import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
m = 2

while True:
    m = GPIO.input(6)
    t = GPIO.input(13)
    print ('input 6:', m)
    print ('input 13:', t)
    time.sleep(2)