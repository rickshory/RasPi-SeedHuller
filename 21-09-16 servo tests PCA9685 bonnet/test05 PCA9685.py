# demo of PCA9685 PWM
# test device addresses, set by jumpers
# strips of conductive adhesive copper foil seem to work as
# moveable jumpers, if ends folded under so top copper
# makes contact on the jumper pads

import smbus
import time
import logging
import math


# PCA9685 registers/etc:
PCA9685_ADDRESS    = 0x40
MODE1              = 0x00
# Bits (*=default)
# 7 RESTART
#    Read: Shows state of RESTART logic. See Section 7.3.1.1 for detail.
#    Write: User writes logic 1 to this bit to clear it to logic 0.
#     A user write of logic 0 will have no effect. See Section 7.3.1.1 for detail.
#    0* Restart disabled.
#    1 Restart enabled.
# 6 EXTCLK
#    R/W To use the EXTCLK pin, this bit must be set by the following sequence:
#    1. Set the SLEEP bit in MODE1. This turns off the internal oscillator.
#    2. Write logic 1s to both the SLEEP and EXTCLK bits in MODE1.
#    The switch is now made. The external clock can be active during the
#    switch because the SLEEP bit is set.
#    This bit is a ‘sticky bit’, that is, it cannot be cleared by writing a
#    logic 0 to it. The EXTCLK bit can only be cleared by a power cycle or
#    software reset. EXTCLK range is DC to 50 MHz.
#    0* Use internal clock.
#    1 Use EXTCLK pin clock.
# 5 AI R/W
#    0* Register Auto-Increment disabled[1].
#    1 Register Auto-Increment enabled.
# 4 SLEEP R/W
#    0 Normal mode[2].
#    1* Low power mode. Oscillator off[3][4].
# 3 SUB1 R/W
#    0* PCA9685 does not respond to I2C-bus subaddress 1.
#    1 PCA9685 responds to I2C-bus subaddress 1.
# 2 SUB2 R/W
#    0* PCA9685 does not respond to I2C-bus subaddress 2.
#    1 PCA9685 responds to I2C-bus subaddress 2.
# 1 SUB3 R/W
#    0* PCA9685 does not respond to I2C-bus subaddress 3.
#    1 PCA9685 responds to I2C-bus subaddress 3.
# 0 ALLCALL R/W
#    0 PCA9685 does not respond to LED All Call I2C-bus address.
#    1* PCA9685 responds to LED All Call I2C-bus address
MODE2              = 0x01
SUBADR1            = 0x02
SUBADR2            = 0x03
SUBADR3            = 0x04

LED0_ON_L          = 0x06
LED0_ON_H          = 0x07
LED0_OFF_L         = 0x08
LED0_OFF_H         = 0x09
ALL_LED_ON_L       = 0xFA
ALL_LED_ON_H       = 0xFB
ALL_LED_OFF_L      = 0xFC
ALL_LED_OFF_H      = 0xFD
PRE_SCALE          = 0xFE  # prescale register for PWM output frequency
# max 1526 Hz = 0x03h
# min 24 Hz = 0xFFh
# PRE_SCALE can only be set when MODE1.SLEEP = 1
# calculate: PRE_SCALE = round(osc/(4096*freq))-1

# (PRE_SCALE Default of 0x1E gives 200 Hz refresh rate at osc 25 MHz)

# Bits:
RESTART            = 0x80
SLEEP              = 0x10
ALLCALL            = 0x01
INVRT              = 0x10
OUTDRV             = 0x04

OSC_CLOCK          = 25000000 # default on-chip, 25 MHz
DESIRED_FREQUENCY  = 200 # in Hz
#DESIRED_FREQUENCY  = 100 # in Hz
#DESIRED_FREQUENCY  = 50 # in Hz

PULSE_MIN          = 1.0 # 0 degrees
PULSE_MID          = 1.5 # 45 degrees
PULSE_MAX          = 2.0 # 90 degrees

prescale_value = round(OSC_CLOCK/(4096 * DESIRED_FREQUENCY)) - 1
print(prescale_value)

i2c_bus = smbus.SMBus(1) # Create a new I2C bus
# *** the following got too complicated
# instead used (from the terminal window)
# i2cdetect -y 1

for addr in range(PCA9685_ADDRESS | 0b00111111, PCA9685_ADDRESS - 1, -1):
# nomenclature from datasheet has highest bit in 7 position, e.g. 0xe0
# nomenclature as used in Python and RPI has highest bit in 6 position, e.g. 0x70
#    if addr == 0xE0: # skip ALLCALLADR register
    if addr == 0x70: # skip ALLCALLADR register
        print("ALLCALLADR register {0} skipped".format(hex(addr)))
        continue

#    if addr == 0b00000110: # skip 'reserved for future use' I2C-bus address
    if addr == 0b00000011: # skip 'reserved for future use' I2C-bus address
        print("reserved register {0} skipped".format(hex(addr)))
        continue

#    if addr >= 0b11111100: # skip 'reserved for future use' I2C-bus address range
    if addr >= 0b01111110: # skip 'reserved for future use' I2C-bus address range
        print("register {0} in reserved range skipped".format(hex(addr)))
        continue
              
    print(hex(addr), addr)
    

### enable PRE_SCALE change, set MODE1.SLEEP = 1
##i2c_bus.write_byte_data(PCA9685_ADDRESS, MODE1, 0x10)
##time.sleep(.25) # delay for reset
##
### set freqency
###i2c_bus.write_byte_data(PCA9685_ADDRESS, PRE_SCALE, 0x1e)
##i2c_bus.write_byte_data(PCA9685_ADDRESS, PRE_SCALE, prescale_value)
##
### enable the PWM chip: clear MODE1.SLEEP bit 4
### auto-increment address after write: set MODE1.AI bit 5
##i2c_bus.write_byte_data(PCA9685_ADDRESS, MODE1, 0x20)
##
### write the time point during each cycle to turn ON 
##i2c_bus.write_word_data(PCA9685_ADDRESS, LED0_ON_L, 0)
##
### write the time point during each cycle to turn OFF
##i2c_bus.write_word_data(PCA9685_ADDRESS, LED0_OFF_L, 1250)
##
##time.sleep(2)
##i2c_bus.write_word_data(PCA9685_ADDRESS, LED0_OFF_L, 1550)




