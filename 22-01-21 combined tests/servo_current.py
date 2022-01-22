# exercise servo motor while monitoring current through it
# servo control using NXP Semiconductors PCA9685 PWM driver chip
# current measurement using TI INA260

# keyboard control of servo
# + and - step up and down one step each
# numbers move up and down by the numeric value entered
# theoretically 200 and 400 are 90 degrees apart
# enter "x" to explicitly end

# initial verson, current monitoring not implemented yet

import smbus, time, logging, math

# PCA9685 registers/etc:
PCA9685_ADDRESS    = 0x40 # address lines A0-A5 all low
MODE1              = 0x00
# 'LED' in PCA9685 datasheet, using 'PWM' here
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
#    0 PCA9685 does not respond to PWM All Call I2C-bus address.
#    1* PCA9685 responds to PWM All Call I2C-bus address
MODE2              = 0x01
SUBADR1            = 0x02
SUBADR2            = 0x03
SUBADR3            = 0x04

PWM0_ON_L          = 0x06
PWM0_ON_H          = 0x07
PWM0_OFF_L         = 0x08
PWM0_OFF_H         = 0x09
ALL_PWM_ON_L       = 0xFA
ALL_PWM_ON_H       = 0xFB
ALL_PWM_OFF_L      = 0xFC
ALL_PWM_OFF_H      = 0xFD
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
#DESIRED_FREQUENCY  = 200 # in Hz
#DESIRED_FREQUENCY  = 100 # in Hz
DESIRED_FREQUENCY  = 50 # in Hz

PULSE_MIN          = 1.0 # 0 degrees
PULSE_MID          = 1.5 # 45 degrees
PULSE_MAX          = 2.0 # 90 degrees

##prescale_value = round(OSC_CLOCK/(4096 * DESIRED_FREQUENCY)) - 1
##print(prescale_value)
# For 50Hz, calculation gives 0x78, but emperically 0x7C is more
# accurate. Still investigating why.
prescale_value = 0x7C
print("prescale value", prescale_value)

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

# write the time point during each cycle to turn ON, 0us
i2c_bus.write_word_data(PCA9685_ADDRESS, PWM0_ON_L, 0)

# write the time point during each cycle to turn OFF
# for 50Hz, should range from about 200 (1ms) to 400 (2ms)
# start about 1.5ms, midrange
time_high = 300
i2c_bus.write_word_data(PCA9685_ADDRESS, PWM0_OFF_L, time_high)
# 1.5ms (45 degrees)


# INA260 registers/etc:
#INA260_ADDRESS = 0x40 # base addreass, A0 and A1 both ground
INA260_ADDRESS = 0x45 # A0 and A1 both VS
TEST_ADDRS = [0x40, 0x41, 0x44, 0x45]
# A0  A1  I2C address
# GND GND 0x40
# VS  GND 0x41
# GND VS  0x44
# VS  VS  0x45
# these, on Adafruit board
# other addresses available by connections to SDA & SCL
# see page 18 of the datasheet

CONFIG_REG = 0x00 # Configuration Register
# All-register reset, shunt voltage & bus voltage ADC conversion times
# averaging, operating mode
# default: 0b01100001 00100111, 0x6127, R/W
CURRENT_REG = 0x01 # the value of the current flowing through
# the shunt resistor
BUS_VOLTAGE_REG = 0x02 # Bus voltage measurement data
PWR_REG = 0x03 # calculated power being delivered to the load
MSK_EN_REG = 0x06 # Mask/Enable Register
# Alert configuration and Conversion Ready flag
ALRT_LIM_REG = 0x07 # Alert Limit Register
# limit value to compare to the selected Alert function
MFR_ID = 0xFE # unique manufacturer identification number
# value: 0b0101010001001001, 0x5449, R
DIE_ID = 0xFF # unique die identification number
# value: 0b0010001001110000, 0x2270, R

# Bits (*=default)
# Configuration Register
#    Can read at any time, no effect. Write cancels any conversion,
#    which restarts on completion, based on new configuration

# 15, RST, R/W, 0*, Reset Bit
#    Setting this bit to '1' generates a system reset that
#    resets all registers to default values; this bit self-clears.
# 14–12, unused, R 110*
# 11–9, AVG, R/W, 000, Averaging Mode
#    number of samples collected and averaged
#    000, samples = 1*
#    001, samples = 4
#    010, samples = 16
#    011, samples = 64
#    100, samples = 128
#    101, samples = 256
#    110, samples = 512
#    111, samples = 1024
# 8–6, VBUSCT, R/W, 100, Bus Voltage Conversion Time
#    000, conversion time = 140 µs
#    001, conversion time = 204 µs
#    010, conversion time = 332 µs
#    011, conversion time = 588 µs
#    100, conversion time = 1.1 ms*
#    101, conversion time = 2.116 ms
#    110, conversion time = 4.156 ms
#    111, conversion time = 8.244 ms
# 5–3 ISHCT R/W 100 Shunt Current Conversion Time
#    000, conversion time = 140 µs
#    001, conversion time = 204 µs
#    010, conversion time = 332 µs
#    011, conversion time = 588 µs
#    100, conversion time = 1.1 ms*
#    101, conversion time = 2.116 ms
#    110, conversion time = 4.156 ms
#    111, conversion time = 8.244 ms
# 2–0 MODE R/W 111 Operating Mode
#    Selects continuous, triggered, or power-down mode of operation.
#    These bits default to continuous shunt and bus measurement mode.
#    000, mode = Power-Down (or Shutdown)
#    001, mode = Shunt Current, Triggered
#    010, mode = Bus Voltage, Triggered
#    011, mode = Shunt Current and Bus Voltage, Triggered
#    100, mode = Power-Down (or Shutdown)
#    101, mode = Shunt Current, Continuous
#    110, mode = Bus Voltage, Continuous
#    111, mode = Shunt Current and Bus Voltage, Continuous*


def read_unsigned_16bit(bus, address, register):
    v = bus.read_word_data(address, register) & 0xFFFF
    # reverse the byte order
    v = ((v << 8) & 0xFF00) + (v >> 8)
    return v

def read_signed_16bit(bus, address, register):
    v = read_unsigned_16bit(bus, address, register)
    if v > 32767:
        v -= 65536
    return v

##print("INA260 manufacturer ID: {0}".
##      format(hex(read_unsigned_16bit(i2c_bus, INA260_ADDRESS, MFR_ID))))
### gets correct 0x5449
##print("INA260 die ID: {0}".
##      format(hex(read_unsigned_16bit(i2c_bus, INA260_ADDRESS, DIE_ID))))
### gets correct 0x2270
##print("INA260 bus voltage: {0}".
##      format(read_signed_16bit(i2c_bus, INA260_ADDRESS, BUS_VOLTAGE_REG)))
while True:
    print("current: {0}".
      format(read_signed_16bit(i2c_bus, INA260_ADDRESS, CURRENT_REG)))

### test manually stepping servo pulse width up and down
##while (1):
##    s = input('--> ')
##    if s == "x":
##        break
##    else:
##        if s == "+":
##            time_high = time_high + 1
##        elif s == "-":
##            time_high = time_high - 1
##        else:
##            try:
##                i = int(s)
##                time_high = time_high + i
##
##            except ValueError:
##                pass
##
##        
##        print("steps in pulse", time_high)
##        i2c_bus.write_word_data(PCA9685_ADDRESS, PWM0_OFF_L, time_high)
    
        

