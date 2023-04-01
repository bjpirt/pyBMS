from machine import I2C, Pin

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


class MCP3421:

    def __init__(self, sda_pin, scl_pin, address=DEFAULT_ADDRESS):
        self.__address = address
        self.__bus = I2C(0, sda=Pin(sda_pin), scl=Pin(scl_pin))
        self.ready = False
        self.__device_search()
        self.__configure()

    def __device_search(self) -> None:
        addresses = self.__bus.scan()
        if self.__address in addresses:
            self.ready = True

    def __configure(self):
        config = CONFIG_RDY_ON | CONFIG_CONV_CONTINUOUS | CONFIG_RATE_3_75SPS | CONFIG_GAIN_X1
        self.__bus.writeto(self.__address, bytes(config))

    def read(self) -> int:
        if self.ready:
            data = self.__bus.readfrom(self.__address, 3)

            return ((data[0] & 0b00000011) << 16) + (data[1] << 8) + data[2]
        else:
            raise Exception("No ADC found")
