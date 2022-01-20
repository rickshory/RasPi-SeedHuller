# demo of INA260
# initial test, get maufacturer ID in correct byte order

import smbus
import time
import logging
import math


# INA260 registers/etc:
INA260_ADDRESS = 0x40 # base addreass, A0 and A1 both ground
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

i2c_bus = smbus.SMBus(1) # Create a new I2C bus

# first test, get manufacturer ID
v = i2c_bus.read_byte_data(INA260_ADDRESS, MFR_ID)
# time.sleep(.25) # delay for reset
print(hex(v))
# gets only the first byte, 0x54
w = i2c_bus.read_word_data(INA260_ADDRESS, MFR_ID)
print(hex(w))
# gets 0x4954, evidently byte order reversed
w = ((w << 8) & 0xFF00) + (w >> 8)
print(hex(w))
# gets correct 0x5449

# *** CAUTION ***
# 'read_block_data' locks up the whole Raspberry Pi
# can't reboot; power cycle loses current python file

##
### todo
##i2c_bus.write_byte_data(INA260_ADDRESS, REG value)
##
### todo
##i2c_bus.write_word_data(INA260_ADDRESS, REG value)
##
##time.sleep(2)





