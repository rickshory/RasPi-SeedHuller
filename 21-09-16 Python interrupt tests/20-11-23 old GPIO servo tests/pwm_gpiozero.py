from gpiozero import Servo
from gpiozero import PWMOutputDevice as PWMo
from time import sleep

p = PWMo
p.pin(18)


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
     


    
