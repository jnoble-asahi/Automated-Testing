import os
import time
import sys
import subprocess
from pipyadc import ADS1256 #Library for interfacing with the ADC via Python
import gpiozero as gz #Library for using the GPIO with python
from ADS1256_definitions import * #Configuration file for the ADC settings
from dac8552.dac8552 import DAC8552, DAC_A, DAC_B, MODE_POWER_DOWN_100K #Library for using the DAC

def start_daemons():
    print('summoning IO daemons')
    bash = "sudo pigpiod" 
    process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    time.sleep(1) # give time for pigpio to start up

def killDaemons():
    print('sacrificing IO daemons') # Kill the IO daemon process
    bash = "sudo killall pigpiod" 
    process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    return (output, error)    

EXT1, EXT2, EXT3, EXT4 = POS_AIN0|NEG_AINCOM, POS_AIN1|NEG_AINCOM, POS_AIN2|NEG_AINCOM, POS_AIN3|NEG_AINCOM
EXT5, EXT6, EXT7, EXT8 = POS_AIN4|NEG_AINCOM, POS_AIN5|NEG_AINCOM, POS_AIN6|NEG_AINCOM, POS_AIN7|NEG_AINCOM

INPUTS_ADDRESS = (EXT1, EXT2, EXT3, EXT4, EXT5, EXT6, EXT7, EXT8)

digital_inputs = (gz.Button(6, pull_up = True), gz.Button(13, pull_up = True), gz.Button(19, pull_up = True))

digital_outputs = (gz.LED(26), gz.LED(20), gz.LED(21))

CH1_Loc = {'cntrl' : DAC_A,
           'mod_out' : DAC_B,
           'relay' : digital_outputs[2],
           'torq' : INPUTS_ADDRESS[0],
           'act_pos' : INPUTS_ADDRESS[1],
           'act_temp' : INPUTS_ADDRESS[2],
           'act_current' : INPUTS_ADDRESS[3],
           'FK_On': digital_inputs[0],
           'FK_Off' : digital_inputs[1]} # GPIO pin numbers

CH_Out = {'1' : DAC_A ,
          '2' : DAC_B}

tests = ('1')

binary = {'INPUT' : 0,
          'OUTPUT': 1,
          'LOW' : 0,
          'HIGH' : 1}

OUTPUT = binary['OUTPUT']
INPUT = binary['INPUT']
LOW = binary['LOW']
HIGH = binary['HIGH']

yes = ('YES', 'yes', 'y', 'Ye', 'Y')
no = ('NO','no', 'n', 'N', 'n')
yes_no = ('YES', 'yes', 'y', 'Ye', 'Y', 'NO','no', 'n', 'N', 'n')
local = ('local', 'Local', 'l')