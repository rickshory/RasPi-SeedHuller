import RPi.GPIO as GPIO
import time

# GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)

STEPPER_PIN_1 = 5
STEPPER_PIN_2 = 6
STEPPER_PIN_3 = 13
STEPPER_PIN_4 = 26

GPIO.setup(STEPPER_PIN_1, GPIO.OUT)
GPIO.output(STEPPER_PIN_1, GPIO.LOW)

while 1:
    GPIO.output(STEPPER_PIN_1, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(STEPPER_PIN_1, GPIO.LOW)
    time.sleep(0.5)
