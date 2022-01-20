# Buzzer motor control using NXP Semiconductors PCA9685 PWM driver chip
# The PCA9685 is designed for PWM dimming of LEDs, which explains why registers
# are named e.g. "LED1_ON_L", but these are just channel numbers and the PWM
# signal works general PWM output

# Three channels, 01, 02, and 03, control a DRV8601 haptic driver
# For first tests, channel outputs are only on/off:
# Channel  DRV8601 pin
#    01       EN
#    02       IN1
#    03       IN2
# EN Low = no output
# EN high, the DRV8601 differential output is according to IN1 and IN2
# IN1 high and IN2 low, output positive, motor spins clockwise
# IN1 low and IN2 high, output negative, motor spins counter clockwise
# (IN1 & IN2 both high or low, to be tested)
# PWM on IN1 and/or IN2, to be tested

# On startup, goes to all lines low
# enter "x" to explicitly end

import smbus, time, logging, math

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

# channel base addresses
# all channels are strictly in increments of 4
# e.g. LED1_ON_L = LED0_ON_L + 4
# e.g. LEDn_ON_L = CHAN_BASE_ADDR_ON_L + 4*n
CHAN_BASE_ADDR_ON_L          = 0x06
CHAN_BASE_ADDR_ON_H          = 0x07
CHAN_BASE_ADDR_OFF_L         = 0x08
CHAN_BASE_ADDR_OFF_H         = 0x09

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

MAX_HIGH = 4095 # maximum of PCA9685 counter
# CHAN_FULL, bit 4, turns a channel full on or off
# written to CHANn_ON_H turns full on
# written to CHANn_OFF_H turns full off
# other bits ignored except for delay in ON
CHAN_FULL = 0x10
states_tpl = ("off", "on")
# key is the code for which signal to control
# val[0] is the channel number, val[1] is the initial state
ctrl_dict = {"en": [1, states_tpl[0]],
             "in1": [2, states_tpl[0]],
             "in2": [3,  states_tpl[0]]}


OSC_CLOCK          = 25000000 # default on-chip, 25 MHz
DESIRED_FREQUENCY  = 200 # in Hz
#DESIRED_FREQUENCY  = 100 # in Hz
#DESIRED_FREQUENCY  = 50 # in Hz

#prescale_value = round(OSC_CLOCK/(4096 * DESIRED_FREQUENCY)) - 1
prescale_value = 0x03 # max, 1525 Hz
print(prescale_value)

i2c_bus = smbus.SMBus(1) # Create a new I2C bus

# enable PRE_SCALE change, set MODE1.SLEEP = 1
i2c_bus.write_byte_data(PCA9685_ADDRESS, MODE1, 0x10)
time.sleep(.25) # delay for reset

# set freqency
#i2c_bus.write_byte_data(PCA9685_ADDRESS, PRE_SCALE, 0x1e)
i2c_bus.write_byte_data(PCA9685_ADDRESS, PRE_SCALE, prescale_value)

# enable the PWM chip: clear MODE1.SLEEP bit 4
# auto-increment address after write: set MODE1.AI bit 5
i2c_bus.write_byte_data(PCA9685_ADDRESS, MODE1, 0x20)

while (1):
    for key in ctrl_dict:
        chan_num = ctrl_dict[key][0]
        chan_state = ctrl_dict[key][1]
        print(key.upper(), "channel",
              chan_num, "is", chan_state)
        state_index = states_tpl.index(chan_state) # 0 or 1
        if state_index == 0: # full off
            # clear ON register, so no conflict
            i2c_bus.write_word_data(PCA9685_ADDRESS,
                    CHAN_BASE_ADDR_ON_H + 4 * chan_num, 0)
            # set full off
            i2c_bus.write_word_data(PCA9685_ADDRESS,
                    CHAN_BASE_ADDR_OFF_H + 4 * chan_num, CHAN_FULL)
        else: # full on
            # clear OFF register so no conflict
            i2c_bus.write_word_data(PCA9685_ADDRESS,
                    CHAN_BASE_ADDR_OFF_H + 4 * chan_num, 0)
            # set low ON register = 0 for no delay
            i2c_bus.write_word_data(PCA9685_ADDRESS,
                    CHAN_BASE_ADDR_ON_L + 4 * chan_num, 0)
            # set full on
            i2c_bus.write_word_data(PCA9685_ADDRESS,
                    CHAN_BASE_ADDR_ON_H + 4 * chan_num, CHAN_FULL)
            
##        # write the time point during each cycle to turn ON, 0us
##        i2c_bus.write_word_data(PCA9685_ADDRESS,
##                CHAN_BASE_ADDR_ON_L + 4 * chan_num, 0)
##        i2c_bus.write_word_data(PCA9685_ADDRESS,
##                CHAN_BASE_ADDR_ON_H + 4 * chan_num, 0)
##        if chan_state == "off":
##            off_pt_val = 1 # turn off in minimal time
##        if chan_state == "on":
##            off_pt_val = MAX_HIGH # stay on for maximal time
##        # set the channel time point to turn off
##        i2c_bus.write_word_data(PCA9685_ADDRESS,
##                CHAN_BASE_ADDR_OFF_L + 4 * chan_num, off_pt_val % 512)
##        i2c_bus.write_word_data(PCA9685_ADDRESS,
##                CHAN_BASE_ADDR_OFF_H + 4 * chan_num, off_pt_val // 512)
    print() # blank line for readablilty

    s = input('Line to toggle ').strip().lower()
    
    if s == "x":
        break
    
    if s in ctrl_dict.keys():
        # toggle
        old_state_index = states_tpl.index(ctrl_dict[s][1]) # 0 or 1
        new_state_index = (old_state_index + 1) % 2
        ctrl_dict[s][1] = states_tpl[new_state_index]

    else:
        print("unrecognized input")
        pass

    
        

