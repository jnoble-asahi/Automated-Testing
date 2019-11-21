'''
Notes on the differences in GPIO pin numbering schemes:
- For a variety of reasons, there's different pin numbering schemes across the GPIO physical header position (the 40 pin connector on the pi)
the pin numbering on the BCM2835 chip, the pin numbering scheme used by the wiringPI module, and the scheme used for the piGPIO module
- The pypiADC module used in this program uses *phys() method to initialize wiringPi. In this case, pin numbers called by wiringPI refer to the
physical location on the GPIO header
- The pigpio module uses the BCM pin numbering scheme, layout here: https://abyz.me.uk/rpi/pigpio/#Type_3
- Compatibility issues may come up in the future as hardware architectures change 
    - The creator of wiringPI made their schema to future proof against changes
- Refer to the layout in the documentation to find the pin numbers under each scheme
- A list of resources for pin numbering here:
    - https://abyz.me.uk/rpi/pigpio/#Type_3
        - pigpio pin numbering schema (based on BCM pinout)
    - http://wiringpi.com/pins/
        - Pin layouts for wiringPI
    - http://wiringpi.com/reference/setup/
        - Overview of the different setup methods available for wiringPI
'''
############################################
''' This is a rough draft of code required to run the actuation tester prototype
The script loads two other programs - ADC_Script and DAC_Script
The project requires a large number of dependencies from other libraries
Full details on dependencies and set-up instructions on Github here: exampleURL.com
Pin callouts in this program refer to the wiringPI addresses and not GPIO pin numbers
This script written by Chris May - pezLyfe on github
######## '''
# Adding a couple of things that need to be worked out later
import os
import pigpio as io
import time
import pandas as pd
import os
import sys
import math as mt
import numpy as np
from ADS1256_definitions import * #Configuration file for the ADC settings
from pipyadc import ADS1256 #Library for interfacing with the ADC via Python
import gpiozero as gz #Library for using the GPIO with python
from dac8552.dac8552 import DAC8552, DAC_A, DAC_B, MODE_POWER_DOWN_100K #Library for using the DAC
import subprocess

# Start the pigpio daemon 
print('summoning IO daemons')
bash = "sudo pigpiod" 
process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

maxRaw = [5625100, 5625100] 
minRaw = [22500, 22500]

ads = ADS1256()
ads.cal_self() 

dac = DAC8552()
print('setting dac')
dac.v_ref = 5
step = dac.digit_per_v
print(dac.v_ref)
print(step)
dac.write_dac(DAC_A, 0*step)
print('data:', 0*step)
print('sleep')
time.sleep(10)
print('powering down dac')
dac.power_down(DAC_A, MODE_POWER_DOWN_100K)

######################## Original Code and Function Definitions from the pipyadc library ################################################
EXT1, EXT2, EXT3, EXT4 = POS_AIN0|NEG_AINCOM, POS_AIN1|NEG_AINCOM, POS_AIN2|NEG_AINCOM, POS_AIN3|NEG_AINCOM
EXT5, EXT6, EXT7, EXT8 = POS_AIN4|NEG_AINCOM, POS_AIN5|NEG_AINCOM, POS_AIN6|NEG_AINCOM, POS_AIN7|NEG_AINCOM

INPUTS_ADDRESS = (EXT1, EXT2, EXT3, EXT4, EXT5, EXT6, EXT7, EXT8)

CH1_Loc = {'pos' : INPUTS_ADDRESS[0],
           'cur' : INPUTS_ADDRESS[2],
           'temp' : INPUTS_ADDRESS[5]}

CH2_Loc = {'pos' : INPUTS_ADDRESS[1],
           'cur' : INPUTS_ADDRESS[3],
           'temp' : INPUTS_ADDRESS[6]}

CH_Out = {'1' : DAC_A ,
          '2' : DAC_B}

CH1_SEQUENCE = (CH1_Loc['pos'], CH1_Loc['cur'], CH1_Loc['temp']) #Position, Current, Temperature channels

CH2_SEQUENCE =  (CH2_Loc['pos'], CH2_Loc['cur'], CH2_Loc['temp']) #Position, Current, Temperature channels

channels = {'1' : CH1_SEQUENCE,
            '2' : CH2_SEQUENCE}

tests = ('1', '2')

class modSample():
    '''
    A class used for modulating actuator tests. Test parameters are read from a .csv file stored locally. Later I'll get updated and these
    parameters will be read remotely. 
    
    In addition to the parameters needed to define the test, this class stores a bunch of variables needed to run the test function
    that's later defined
    '''
    def __init__(self):
        self.position = 0
        self.stamp = time.time()
        self.lastTime = time.time() - self.stamp # Timestamp for the last datalog recording
        self.positions = [] # List of positions the actuator has been in
        self.currents = [] # List of current readings from the current sensor assigned
        self.temps = [] # List of temperature readings from temp sensor assigned
        self.cts = [] # List containing the length of each cycle, in seconds
        self.torSensor = [] # List containing the torque readings
        self.setpoints = [] # List containing the setpoints the actuator went to
        self.slack = 2 # Allowable position offset from the setpoint
        self.wait = 1.5 # Wait time between position readings
        self.cycles = int(0) # Number of cycles completed
        self.wt = time.time() # A timestamp of when the current cycle started
        self.sp = 100
        self.measureRate = 60
        self.lastMeasure = time.time()

    def newTest(self, chan):
        self.pinsIn = channels[chan]
        self.pinOut = CH_Out[chan]
        self.active = True
        self.name = chan

def positionMeasurement(chanIn):
    '''
    Read an ADC input and linearize the raw input to a position value of 0 - 100%
    '''
    x = ads.read_oneshot(chanIn) #Read the raw integer input on the channels
    y = ((float(x - minRaw)) / maxRaw)*100
    return(y)

def positionConvert(pos, chan):
    '''Take the raw value from a position measurment and convert that to a value of 0 - 100%
    '''
    x = (1.55991453001704*10**-5 * pos - 0.35929652281208746) #This conversion only holds for the current installation
    return(x)

def rawConvert(y):
    '''
    Linearization function for converting position readings to raw digital readings
    Position readings vary from 0 - 100%, and the raw readings vary from 0 to 8,388,608
    '''
    x = (y * 64000) + minRaw
    return(x)

def currentMeasurement(chanIn):
    '''
    Read and linearize a current input to Amps
    '''
    x = ads.read_oneshot(chanIn) #Read the raw integer input on the channels
    y = float(x * ads.v_per_digit)
    current = (2.5 - y) * 186
    return(current)

def currentConvert(curr):
    '''Linearize a raw current input reading
    '''
    x = (2.5 - float(curr * ads.v_per_digit))*186
    return(x)

def tempMeasurement(chanIn):
    '''
    Convert temperature readings from the J type thermocouple into a readable format
    '''
    x = ads.read_oneshot(chanIn) #Read the raw integer input on the channels
    y = float(x * ads.v_per_digit)
    temp = (y - 1.25) / 0.005
    return(temp)

def tempConvert(temp):
    '''Convert a temperature reading from the J type thermocouple in a fahrenheit reading
    '''
    x = float(temp * ads.v_per_digit)
    y = (x- 1.25)/ 0.005
    return(y)
    
def torqueMeasurement(inputs):
    raw_channels = ads.read_sequence(inputs)
    torSens = raw_channels[0]
    tor = torqueConvert(torSens)
    return(tor)

def torqueConvert(tor):
    torqueVal = (tor - 4)*6000/16 #convert 4-20 mA indicator signal to torque reading in in-lbs
    return(torqueVal)

def single_measurement(chanIn):
    '''Read the input voltages from the ADC inputs, returns as a raw integer value
    '''
    raw_channels = ads.read_oneshot(chanIn) #Read the raw integer input on the channels
    return(raw_channels)

def modulate(modChan):
    aOut = int(np.random.randint(0, high = dac.v_ref) * dac.digit_per_v) #Default arguments of none for size, and I for dtype (single value, and int for data type)
    dac.write_dac(modChan, aOut)
    aPos = int((float(aOut) / (dac.v_ref * dac.digit_per_v)) * 100)
    print( modChan, ' to Random', aPos)
    return(aPos)

def do_measurement(inputs, chan):
    '''Read the input voltages from the ADC inputs. The sequence that the channels are read are defined in the configuration files
    Voltages are converted from the raw integer inputs using a voltage convert function in the pipyadc library
    The conversion to current readings is given from the datasheet for the current module by sparkfun
    '''
    raw_channels = ads.read_sequence(inputs) #Read the raw integer input on the channels defined in read_sequence
    pos_channel = int(positionConvert(raw_channels[0], chan))
    curr = int(currentConvert(raw_channels[1]))
    temp = tempConvert(raw_channels[2])
    return(pos_channel, curr, temp, time.time())

def onOff_measurement(inputs):
    '''
    Read the input voltages from the current and temperature inputs on the ADC. 
    Voltages are convereted from raw integer inputs using convert functions in this library
    '''
    raw_channels = ads.read_sequence(inputs)
    curr = raw_channels[1]
    #temp = raw_channels[2]
    return(curr)

def curTempRead(inputs):
    '''Read the input voltages from ADC inputs specifically for temperature and current
    '''
    raw_channels = ads.read_sequence(inputs) #Read the raw integer input on the channels defined in read_sequence
    return(raw_channels)

def modMeasure(target):
    '''
    Measures position, current draw, temperature from the target, and appends them to a list in target.parameter
    Calculates the difference in time between now and the last time the data was written to csv
    '''
    if target.cycles < 1000000:
        posRead = int(positionConvert(single_measurement(target.pinsIn[0]),1))
        curRead = single_measurement(target.pinsIn[1])
        tempRead = single_measurement(target.pinsIn[2])
        target.position = posRead
        target.positions.append(posRead)
        target.currents.append(curRead)
        target.temps.append(tempRead)
        target.cts.append(time.time())
        target.setpoints.append(target.sp)
        target.lastTime = time.time() - target.stamp
    else:
        target.active = False

def posCheck(target):
    '''
    Check the current position of the actuator. If it's within +/- 2% of the setpoint, change the setpoint
    If it's not, open the tolerance slightly, and increase the wait time a little bit
    Print a status message
    '''
    target.position = int(positionConvert(single_measurement(target.pinsIn[0]),1))
    if (time.time() - target.wt > target.wait):
        if target.position in range(int(target.sp - target.slack), int(target.sp + target.slack)):
            print("setpoint reached on {0}".format(target.name))
            time.sleep(5)
            target.sp = modulate(target.pinOut)
            target.wt = time.time()
            target.cycles += 1
            target.wait = 1.5
            target.slack = 2
            print("Channel {0} cycle number is {1}, waiting {2:1.1f} seconds".format(target.name, target.cycles, target.wait))
        else:
            target.wait = target.wait * 1.75
            target.slack = target.slack * 1.10
            print("wait time is {0:0.1f}, Channel {1} Setpoint is {2:0.1f} < {3:0.1f} < {4:0.1f}, waiting {5:1.1f} seconds".format(target.wait, target.name, \
            (target.sp - target.slack), target.position, (target.sp + target.slack), target.wait ))
            time.sleep(1)
    else:
        pass

def logCheck(target):
    '''
    Check if it's been longer than an hour since the last time data was written to a csv
    If it has been longer, write target data to a csv file and update the timestamp
    '''
    if target.lastTime > 3600:
        logData(target)
        target.stamp = time.time()
    else:
        pass

def logData(target):
    df = pd.DataFrame({'time' : target.cts,
                        'Positions' : target.positions,
                        'Current' : target.currents,
                        'Temperature' : target.temps,
                        'Set Point' : target.setpoints})
    df.to_csv("act{}.csv".format(target.name), sep = ',')