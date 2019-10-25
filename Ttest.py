import os
import time
import wiringpi as wp
import pigpio as io # pigpio daemon
import sys
import subprocess

# Initialise Pi connection
pi = io.pi()
if not pi.connected: # exit script if no connection
    print('Unnable to connect to pi')
    exit()

# Start the pigpio daemon 
# bash = "sudo pigpiod" 
# process = subprocess.Popen(bash.split(), stdout=subprocess.PIPE)
# output, error = process.communicate()

#Declare pin outputs and inputs
wp.pinmode(wpi.25, OUTPUT) # Blue test running LED
wp.pinmode(wpi.38, OUTPUT) #Red fault LED
wp.pinmode(3, OUTPUT) # Brake control setpoint
wp.pinmode(4, INPUT) # Transducer signal

# Set Test setpoints
# Brake setpoint (VDC)
print('Enter brake VDC setpoint (0-10VDC)')
setpoint = -1
while True:
    setpoint = raw_input() # prompt user for 0-10 VDC brake setpoint
    #check if setpoint is valid
    if setpoint >= 0 & <= 10:
        break
    else
        print('Entry not valid. Enter number between 0 and 10')
# Test Length (cycles)
print('Enter length of test (number of cycles)')
testLength = 0
while True:
    testLength = raw_input() #prompt user for number of cycles in test
    if testLength > 0:
        break
    else
        print('Invalid entry. Enter number greater than 0.')

#Start Test
wp.digitalWrite (25, HIGH) # Turn on test running light (blue)
wp.analogWrite(3, setpoint) # turn on brake
#wp.analogWrite(5, actuator) # turn on actuator
t = timegm() #test run start time
delay(1000) # Give a second for actuator to start up and create a torque on the sensor
wp.analogRead (4) # Record torque - read continuously figure out how I want to loop it/how often to read it...

#Run and Record data
cycles = int(0) # number of completed actuator cycles
while testLength > cycles:
    #count cycles and end program once amount of cycles reached
  
