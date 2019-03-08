from gpiozero import LED
from time import sleep

led = LED(17)

while True:
    print('on')
    sleep(1)
    print('off')
    sleep(1)