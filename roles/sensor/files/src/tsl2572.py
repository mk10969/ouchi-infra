#!/usr/bin/env python3
"""
TSL2572 Control Module via I2C
 2018/11/15
"""

from datetime import datetime
import smbus
import time


class TSL2572:
    AGAIN_0_16 = 0
    AGAIN_1 = 1
    AGAIN_8 = 2
    AGAIN_16 = 3
    AGAIN_120 = 4

    ATIME_50MS = 0xED
    ATIME_200MS = 0xB6
    ATIME_600MS = 0x24

    def __init__(self, i2c_addr):
        self.i2c_addr = i2c_addr
        self.i2c = smbus.SMBus(1)
        self.ch0 = 0
        self.ch1 = 0
        self.lux = 0
        self.again = TSL2572.AGAIN_8
        self.atime = TSL2572.ATIME_200MS

    # I2C read length byte from addr
    def read_address(self, addr, length):
        addr = addr | 0xA0
        try:
            return self.i2c.read_i2c_block_data(self.i2c_addr, addr, length)
        except IOError:
            return [0 for i in range(length)]

    # I2C write data to addr
    def write_address(self, addr, data):
        addr = addr | 0xA0
        self.i2c.write_i2c_block_data(self.i2c_addr, addr, data)

    # Read ID and return True if success
    def id_read(self):
        data = self.read_address(0x12, 1)
        # Return true if TSL25721 (3.3V). Change to 0x3D if TSL25723 (1.8V).
        if data[0] == 0x34:
            return True
        return False

    def set_atime(self, atime):
        self.write_address(0x1, [atime])

    def set_again(self, again):
        if TSL2572.AGAIN_0_16 == again:
            self.write_address(0xD, [0x4])
            self.write_address(0xF, [0])
        elif TSL2572.AGAIN_1 == again:
            self.write_address(0xD, [0])
            self.write_address(0xF, [0])
        elif TSL2572.AGAIN_8 == again:
            self.write_address(0xD, [0])
            self.write_address(0xF, [0x1])
        elif TSL2572.AGAIN_16 == again:
            self.write_address(0xD, [0])
            self.write_address(0xF, [0x2])
        elif TSL2572.AGAIN_120 == again:
            self.write_address(0xD, [0])
            self.write_address(0xF, [0x3])

    # Read status register
    #  Return avalid, aint as 0 or 1
    def read_status(self):
        data = self.read_address(0x13, 1)
        avalid = data[0] & 0x1
        aint = (data[0] & 0x10) >> 4
        return avalid, aint

    # One time ALS integration and update ch0 and ch1
    def als_integration(self):
        self.write_address(0x0, [0x1])  # Stop ALS integration
        self.set_again(self.again)
        self.set_atime(self.atime)
        self.write_address(0x0, [0x3])  # Start ALS integration

        # Check status every 10ms
        while True:
            avalid, aint = self.read_status()
            if avalid == 1 and aint == 1:
                self.write_address(0x0, [0x1])  # Stop ALS integration
                break
            else:
                time.sleep(0.01)

        data = self.read_address(0x14, 4)
        self.ch0 = (data[1] << 8) | data[0]
        self.ch1 = (data[3] << 8) | data[2]

    # One time lux measurement
    #  Run ALS integration with auto again/atime and calculate lux
    #  Select below again/atime automatically based on default measurement result
    #  again, atime, scale, max count
    #   0.16,    50,  0.04,     19456
    #      1,   200,     1,     65535  (Default)
    #      8,   200,     8,     65535
    #    120,   200,   120,     65535
    #    120,   600,   360,     65535
    def meas_single(self):
        if not self.id_read():
            return False

        self.again = TSL2572.AGAIN_1
        self.atime = TSL2572.ATIME_200MS
        self.als_integration()
        if max([self.ch0, self.ch1]) == 65535:
            self.again = TSL2572.AGAIN_0_16
            self.atime = TSL2572.ATIME_50MS
            self.als_integration()
        elif max([self.ch0, self.ch1]) < 100:
            self.again = TSL2572.AGAIN_120
            self.atime = TSL2572.ATIME_600MS
            self.als_integration()
        elif max([self.ch0, self.ch1]) < 300:
            self.again = TSL2572.AGAIN_120
            self.atime = TSL2572.ATIME_200MS
            self.als_integration()
        elif max([self.ch0, self.ch1]) < 3000:
            self.again = TSL2572.AGAIN_8
            self.atime = TSL2572.ATIME_200MS
            self.als_integration()
        self.write_address(0x0, [0x0])  # Sleep
        self.calc_lux()
        return True

    # Calculate lux from ch0/ch0 then update lux
    def calc_lux(self):
        if TSL2572.ATIME_50MS == self.atime:
            t = 50
        elif TSL2572.ATIME_200MS == self.atime:
            t = 200
        elif TSL2572.ATIME_600MS == self.atime:
            t = 600

        if TSL2572.AGAIN_0_16 == self.again:
            g = 0.16
        elif TSL2572.AGAIN_1 == self.again:
            g = 1
        elif TSL2572.AGAIN_8 == self.again:
            g = 8
        elif TSL2572.AGAIN_16 == self.again:
            g = 16
        elif TSL2572.AGAIN_120 == self.again:
            g = 120

        cpl = (t * g) / 60
        lux1 = (self.ch0 - 1.87 * self.ch1) / cpl
        lux2 = (0.63 * self.ch0 - self.ch1) / cpl

        self.lux = max([0, lux1, lux2])

    # Print atime, again setting and ch0/ch1 data
    def print_reg(self):
        if TSL2572.ATIME_50MS == self.atime:
            print(' ADC Time : 50ms')
        elif TSL2572.ATIME_200MS == self.atime:
            print(' ADC Time : 200ms')
        elif TSL2572.ATIME_600MS == self.atime:
            print(' ADC Time : 600ms')

        if TSL2572.AGAIN_0_16 == self.again:
            print(' ADC Gain : 0.16')
        elif TSL2572.AGAIN_1 == self.again:
            print(' ADC Gain : 1')
        elif TSL2572.AGAIN_8 == self.again:
            print(' ADC Gain : 8')
        elif TSL2572.AGAIN_16 == self.again:
            print(' ADC Gain : 16')
        elif TSL2572.AGAIN_120 == self.again:
            print(' ADC Gain : 120')

        print(' ch0 : 0x{:X}'.format(self.ch0))
        print(' ch1 : 0x{:X}'.format(self.ch1))

    # Print lux
    def print_meas(self):
        print(' Lux : {:.1f}lux'.format(self.lux))

    def to_json(self) -> dict:
        return {
            'timestamp': datetime.now().timestamp(),
            'lux': self.lux,
            'luxUnit': 'lux'
        }


def get_lux() -> dict:
    tsl2572 = TSL2572(0x39)
    if tsl2572.id_read():
        tsl2572.meas_single()
        return tsl2572.to_json()
    else:
        raise RuntimeError('tsl2572: ID Read Failed')


if __name__ == '__main__':
    print(get_lux())
