from hal import I2C, Pin
from hal.interval import get_interval

DEFAULT_ADDRESS = 0x68

# Config Parameter
# Config Parameter RDY_ON  : 0b10000000
CONFIG_RDY_ON = 0x80
# Config Parameter RDY_OFF : 0b00000000
CONFIG_RDY_OFF = 0x00

# Config Parameter ONE_SHOT   : 0b00000000
CONFIG_CONV_ONE_SHOT = 0x00
# Config Parameter CONTINUOUS : 0b00010000
CONFIG_CONV_CONTINUOUS = 0x10

# Config Parameter RATE 240SPS  : 0b00000000
CONFIG_RATE_240SPS = 0x00
# Config Parameter RATE 60SPS   : 0b00000100
CONFIG_RATE_60SPS = 0x04
# Config Parameter RATE 15SPS   : 0b00001000
CONFIG_RATE_15SPS = 0x08
# Config Parameter RATE 3.75SPS : 0b00001100
CONFIG_RATE_3_75SPS = 0x0c

# Config Parameter GAIN X1 : 0b00000000
CONFIG_GAIN_X1 = 0x00
# Config Parameter GAIN X2 : 0b00000001
CONFIG_GAIN_X2 = 0x01
# Config Parameter GAIN X4 : 0b00000010
CONFIG_GAIN_X4 = 0x02
# Config Parameter GAIN X8 : 0b00000011
CONFIG_GAIN_X8 = 0x03


def twos_complement(value, bits):
    if (value & (1 << (bits - 1))) != 0:
        value = value - (1 << bits)
    return value

class MCP3421:

    def __init__(self, sda_pin, scl_pin, address=DEFAULT_ADDRESS, sample_rate=CONFIG_RATE_3_75SPS, gain=CONFIG_GAIN_X1):
        self.__address = address
        self.__bus = I2C(0, sda=Pin(sda_pin), scl=Pin(scl_pin))
        self.__gain = gain
        self.__sample_rate = sample_rate
        self.__last_value: float = 0.0
        self.__interval = get_interval()
        self.__interval.set(self.__sample_period())
        self.ready = False
        self.__device_search()
        self.__configure()

    def __sample_period(self) -> float:
        per_second = 240 >> ((self.__sample_rate >> 2) * 2)
        return 1 / per_second

    def __device_search(self) -> None:
        addresses = self.__bus.scan()
        if self.__address in addresses:
            self.ready = True

    def __configure(self):
        config = CONFIG_RDY_ON | CONFIG_CONV_CONTINUOUS | self.__sample_rate | self.__gain
        self.__bus.writeto(self.__address, bytearray([config]))

    def read(self) -> float:
        if self.ready:
            if not self.__interval.ready:
                return self.__last_value

            self.__interval.reset()
            if self.__sample_rate == CONFIG_RATE_3_75SPS:
                data = self.__bus.readfrom(self.__address, 3)
                rawValue = ((data[0] & 0b00000011) << 16) + (data[1] << 8) + data[2]
                value = twos_complement(rawValue, 18)
            else:
                data = self.__bus.readfrom(self.__address, 2)
                rawValue =  (data[0] << 8) + data[1]
                value = twos_complement(rawValue, 16)
            scaled_value = (value / 0x1FFFF) * 2.048
            self.__last_value = scaled_value
            return scaled_value
        else:
            raise RuntimeError("No ADC found")
