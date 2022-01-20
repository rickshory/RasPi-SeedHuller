# demo of PCA9685 PWM
#  developed using SparkFun tutorial
#  https://learn.sparkfun.com/tutorials/pi-servo-hat-hookup-guide/all
# moves the servo to approximately half-position

import smbus
import logging
import math


# PCA9685 registers/etc:
PCA9685_ADDRESS    = 0x40
MODE1              = 0x00
MODE2              = 0x01
SUBADR1            = 0x02
SUBADR2            = 0x03
SUBADR3            = 0x04
PRESCALE           = 0xFE  #prescaler for PWM output frequency
LED0_ON_L          = 0x06
LED0_ON_H          = 0x07
LED0_OFF_L         = 0x08
LED0_OFF_H         = 0x09
ALL_LED_ON_L       = 0xFA
ALL_LED_ON_H       = 0xFB
ALL_LED_OFF_L      = 0xFC
ALL_LED_OFF_H      = 0xFD

# Bits:
RESTART            = 0x80
SLEEP              = 0x10
ALLCALL            = 0x01
INVRT              = 0x10
OUTDRV             = 0x04

i2c_bus = smbus.SMBus(1) # Create a new I2C bus

# enable the PWM chip
i2c_bus.write_byte_data(PCA9685_ADDRESS, 0, 0x20)
#  tell it to automatically increment addresses after a write 
i2c_bus.write_byte_data(PCA9685_ADDRESS, 0xfe, 0x1e)

# write the time point during each cycle to turn ON 
i2c_bus.write_word_data(PCA9685_ADDRESS, LED0_ON_L, 0)

# write the time point during each cycle to turn OFF
i2c_bus.write_word_data(PCA9685_ADDRESS, LED0_OFF_L, 1250)







