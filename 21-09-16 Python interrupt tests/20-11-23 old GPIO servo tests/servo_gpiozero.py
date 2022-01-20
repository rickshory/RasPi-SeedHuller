from gpiozero import Servo
from time import sleep

servo = Servo(18)
print 'min'
servo.min()
sleep(3)
print 'mid'
servo.mid()
sleep(3)
print 'max'
servo.max()
sleep(3)
servo.detach()
     


    
