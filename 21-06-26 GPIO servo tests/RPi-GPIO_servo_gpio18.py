import RPi.GPIO as GPIO
from time import sleep
from RPIO import PWM


board_pin = 12 # BOARD pin 12 = GPIO18
use_pin = board_pin

def SetAngle(angle):
    duty = angle / 18 + 2
    GPIO.output(use_pin, True)
    pwm.ChangeDutyCycle(duty)
    sleep(3)
    GPIO.output(use_pin, False)
    pwm.ChangeDutyCycle(0)

def SetDuty(duty):
    GPIO.output(use_pin, True)
    pwm.ChangeDutyCycle(duty)
    sleep(3)
    GPIO.output(use_pin, False)
    pwm.ChangeDutyCycle(0)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(use_pin, GPIO.OUT)
pwm=GPIO.PWM(use_pin, 50)
pwm.start(0)
for x in range(3, 14):
    print ("Duty cycle %d " % (x))
    SetDuty(x)
pwm.stop()
GPIO.cleanup()


    
