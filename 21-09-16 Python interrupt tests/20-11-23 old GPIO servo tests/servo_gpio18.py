import RPi.GPIO as GPIO
from time import sleep
from RPIO import PWM

def SetAngle(angle):
    duty = angle / 18 + 2
    GPIO.output(03, True)
    pwm.ChangeDutyCycle(duty)
    sleep(3)
    GPIO.output(03, False)
    pwm.ChangeDutyCycle(0)

def SetDuty(duty):
    GPIO.output(03, True)
    pwm.ChangeDutyCycle(duty)
    sleep(3)
    GPIO.output(03, False)
    pwm.ChangeDutyCycle(0)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(03, GPIO.OUT)
pwm=GPIO.PWM(03, 50)
pwm.start(0)
for x in range(3, 14):
    print "Duty cycle %d " % (x)
    SetDuty(x)
pwm.stop()
GPIO.cleanup()


    
