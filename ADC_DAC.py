from myModule import *
import time

print("Intialize AD/DA Board", myInitFunction())
to=time.time()
delT=0.001;
ii=0;
init=0
while (ii<20):
t1=time.time()
delT=t1-to
if delT>=0.001: 
if ii>0: 
init=1
sensors=myMainFunction(init, 5.0)
to=t1
print("Result:", sensors, "time:",delT)
ii=ii+1

print("Closing Communication", myClosingFunction())