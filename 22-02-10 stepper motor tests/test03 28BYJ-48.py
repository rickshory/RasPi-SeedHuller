import RPi.GPIO as GPIO
import time

# GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)

stepper_pins = [5, 6, 13, 26]

for p in stepper_pins:
    GPIO.setup(p, GPIO.OUT)

for n in range(10):
    time.sleep(0.5)
    for a in range(4):
        for i, p in enumerate(stepper_pins):
            if i == a:
                GPIO.output(p, GPIO.HIGH)
            else:
                GPIO.output(p, GPIO.LOW)
    
        
GPIO.cleanup()
    
