# Buzzer motor control using NXP Semiconductors PCA9685 PWM driver chip
# and DRV8601 haptic driver
# The PCA9685 has 16 output channels designed for PWM dimming of LEDs
# repurposed as high/low outputs

# This version to test combinations of below operations, such as
# multiple toggles in order to reverse motor direction 

# Three channels, 01, 02, and 03, control a DRV8601 haptic driver
# Used on/off (may test signal outputs later):
# Channel  DRV8601 pin
#    01       EN
#    02       IN1
#    03       IN2
# EN Low = no output
# EN high, the DRV8601 differential output is according to IN1 and IN2
# IN1 high and IN2 low, output positive, motor spins clockwise
# IN1 low and IN2 high, output negative, motor spins counter clockwise
# (IN1 & IN2 both high or low, output positive, but less than
# full voltage, not sure why
# PWM on IN1 and/or IN2, to be tested

# On startup, goes to all lines low
# enter "x" to explicitly end

import smbus, time, logging, math

# PCA9685 registers/etc:
PCA9685_ADDRESS    = 0x40
MODE1              = 0x00
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
CHAN_FULL = 0x10
states_tpl = ("off", "on")
# key is the code for which signal to control
# val[0] is the channel number, val[1] is the initial state
toggle_dict = {"en": [1, states_tpl[0]],
             "in1": [2, states_tpl[0]],
             "in2": [3,  states_tpl[0]]}
# try out different functions
fn_dict = {"<>": "reverse"}


OSC_CLOCK          = 25000000 # default on-chip, 25 MHz
DESIRED_FREQUENCY  = 200 # in Hz
#DESIRED_FREQUENCY  = 100 # in Hz
#DESIRED_FREQUENCY  = 50 # in Hz

        
def toggle_state(st):
    # toggle
    global toggle_dict
    old_state_index = states_tpl.index(toggle_dict[st][1]) # 0 or 1
    new_state_index = (old_state_index + 1) % 2
    toggle_dict[st][1] = states_tpl[new_state_index]

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
    for key in sorted(toggle_dict):
        chan_num = toggle_dict[key][0]
        chan_state = toggle_dict[key][1]
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

    print() # blank line for readablilty

    s = input('Line to toggle ').strip().lower()
    
    if s == "x":
        break
    
    if s in toggle_dict.keys():
        toggle_state(s)
        
    elif s in fn_dict.keys():
        if s == "<>": # reverse the motor
            # make this really conservative to begin with
            if toggle_dict["en"][1] == "off":
                print("motor not enabled")
                print()
            if toggle_dict["en"][1] == "on":
                if toggle_dict["in1"][1] == toggle_dict["in2"][1]:
                    print("inputs not configured")
                    print()
                else:
                    toggle_state("in1")
                    toggle_state("in2")
        

    else:
        print("unrecognized input")
        pass

    


    
    
