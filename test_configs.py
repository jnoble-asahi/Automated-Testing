import os
import time
import numpy as np
import system_tools as st
from ADS1256_definitions import * #Configuration file for the ADC settings
from dac8552.dac8552 import DAC8552, DAC_A, DAC_B, MODE_POWER_DOWN_100K #Library for using the DAC
from pipyadc import ADS1256 #Library for interfacing with the ADC via Python
import gpiozero as gz #Library for using the GPIO with python

ads = ADS1256()
dac = DAC8552()
ads.cal_self() 

CH1_Loc = st.CH1_Loc

CH1_SEQUENCE = (CH1_Loc['act_pos'], CH1_Loc['act_current'], CH1_Loc['act_temp']) #Position, Current, Temperature channels
OUTPUT, INPUT, HIGH, LOW = st.OUTPUT, st.INPUT, st.HIGH, st.LOW

maxRaw = [5625100, 5625100] 
minRaw = [22500, 22500]

def set_on_off(test, channelID):
        test.name = channelID
        test.active = True
        print('Reseting variable values in the cloud')
        test.bounces = 0
        test.torque = []
        test.pv = 0
        test.time = []

        # Set up channels
        test.cntrl_channel = CH1_Loc['cntrl']
        test.relay_channel = CH1_Loc['relay']
        test.input_on_channel = CH1_Loc['FK_On']
        test.input_off_channel = CH1_Loc['FK_Off']
        test.output_channel = CH1_Loc['torq']
        test.position_channel = CH1_Loc['act_pos']
        test.temp_channel = CH1_Loc['act_temp']
        test.current_channel = CH1_Loc['act_current']

        # Store current switch states for later
        test.open_last_state = test.input_off_channel.value 
        test.closed_last_state = test.input_on_channel.value

class modSample():
    '''
    A class used for modulating actuator tests. Test parameters are read from a .csv file stored locally. Later I'll get updated and these
    parameters will be read remotely. 
    
    In addition to the parameters needed to define the test, this class stores a bunch of variables needed to run the test function
    that's later defined
    
    def __init__(self):
        self.position = 0
        self.stamp = time.time()
        self.lastTime = time.time() - self.stamp # Timestamp for the last datalog recording
        self.positions = [] # List of positions the actuator has been in
        self.currents = [] # List of current readings from the current sensor assigned
        self.temps = [] # List of temperature readings from temp sensor assigned
        self.cts = [] # List containing the length of each cycle, in seconds
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
        '''

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

def on_off_measurement(inputs):
    '''
    Read the input voltages from the current and temperature inputs on the ADC. 
    Voltages are converted from raw integer inputs using convert functions in this library
    '''
    raw_channels = ads.read_sequence(inputs)
    curr, temp, pos = raw_channels[1], raw_channels[2], raw_channels[3]
    return(curr, temp, pos)

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

def restCalc(length, dCycle):
    '''
    Calculate a new cycle time using the length of the last half cycle, and the duty cycle setting of the test 
    '''
    rest = float(length / (float(dCycle)/100))
    return(rest)

def switchCheck(test):
    '''
    Read the state of the actuator limit switch inputs
    If they changed, do some stuff, if they haven't changed, then do nothing '''

    if (test.pv > test.target): # Check to see if the current cycle count is less than the target
        test.active = False

    else:
        pass

    if test.active != True:
        pass

    else:
        open_state = test.input_on_channel.value
        closed_state = test.input_off_channel.value

        if (test.open_last_state == LOW) & (open_state == HIGH) & (closed_state == HIGH): # Check if changed from fully open position to closing (moving)
            test.open_last_state = HIGH # Reset the "open last state" of the switch
            length = time.time() - test.cycle_start # Calculate the length of the last duty cycle

            if (length > (test.duty_cycle*.49)):
                test.cycle_start = time.time() # update cycle start time
                print('cycle start updated to: ', test.cycle_start) # debugging
                test.pv+= 1 # Increment the pv counter if the switch changed
                # piece for appending test cycle time to a list
                print('test.pv: ', test.pv)
                print("Switch {} confirmed. Actuator is closing.".format(test.name))
                return(1)

            else:
                test.bounces = test.bounces + 1
                print("Switch bounced. Bounce count: {}.".format(test.bounces))
                return(0)

        elif (test.closed_last_state == LOW) & (closed_state == HIGH) & (open_state == HIGH): # Check if changed from fully closed position to opening (moving)
            test.closed_last_state = HIGH # Reset the "closed last state" of the switch
            length = time.time() - test.cycle_start # Calculate the length of the last duty cycle
            print('open state: ', open_state)
            print('closed state: ', closed_state)

            if (length > (test.duty_cycle*.5)):
                test.cycle_start = time.time() # Update cycle start time
                test.pv+= 1 # Increment the pv counter if the switch changed
                print('test.pv: ', test.pv)
                print("Switch {} confirmed. Actuator is opening.".format(test.name))
                return(1)

            else:
                test.bounces = test.bounces + 1
                print("Switch bounced. Bounce count: {}.".format(test.bounces))
                return(0)

        elif (test.open_last_state == HIGH) & (open_state == LOW) & (closed_state == HIGH): # Check to see if recently in fully open position
            print("Switch changed. Actuator is in fully open position.")
            test.open_last_state = LOW # Update last switch state
            test.cycle_time = time.time() - test.cycle_start # Update cycle_time
            print('test.cycle_time updated to: ', test.cycle_time)
            print('open state: ', open_state)
            print('closed state: ', closed_state)
            return(0)

        elif (test.closed_last_state == HIGH) & (closed_state == LOW) & (open_state == HIGH): # Check to see if recently in fully closed position
            print("Switch changed. Actuator is in fully closed position.")
            test.closed_last_state = LOW # Update last switch state
            test.cycle_time = time.time() - test.cycle_start # Update cycle_time
            print('test.cycle_time updated to: ', test.cycle_time)
            print('open state: ', open_state)
            print('closed state: ', closed_state)
            return(0)

        else:
            pass

def cycleCheck(test_channel):
    '''
    Run a series of checks against the current time, the relay states, and actuator information
    Do something based on the results of those checks

    Sensor measurements are taken on the close -> open cycle since that's the point where actuator loads are the highest
    '''
    if test_channel.active != True: # If the test channel isn't currently active, pass
        pass

    elif (test_channel.pv > test_channel.target): # Check to see if the current cycle count is less than the target
        test_channel.active = False # If the pv has been reached, set the channel to inactive

    elif (time.time() - test_channel.cycle_start) > (test_channel.cycle_time): # Check to see if the current cycle has gone past the cycle time
        
        if test_channel.chan_state == HIGH: # If both are yes, change the relay state, and update cycle parameters
            test_channel.relay_channel.off()
            test_channel.chan_state = LOW
            test_channel.cycle_start = time.time()
            print("actuator {} closing".format(test_channel.name))
            time.sleep(0.1)
        
        elif test_channel.chan_state == LOW: #If the actuator recently closed, change the relay state, then take some measurements
            test_channel.relay_channel.on()
            test_channel.chan_state = HIGH
            test_channel.cycle_start = time.time()
            test_channel.shot_count = test_channel.shot_count + 1
            print("Actuator {} opening".format(test_channel.name))
            x = on_off_measurement(CH1_SEQUENCE)
            test_channel.pos.append(x[0])
            test_channel.currents.append(x[1])
            test_channel.temps.append(x[2])
        
        else:
            print("Something's done messed up") # If the switch states don't match the top two conditions, somehow it went wrong
            test_channel.chanState = LOW
            test_channel.cycleStart = time.time()
            time.sleep(0.1)

def logCheck(testChannel):
    if (time.time() - testChannel.last_log) < (testChannel.print_rate):
        pass
    
    elif testChannel.active == False:
        pass
    
    elif testChannel.active == True:
        testChannel.update_db()
        testChannel.last_log = time.time()
    
    else:
        raise Warning("You didn't catch all of the cases")
    








