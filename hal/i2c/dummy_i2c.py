from hal import Pin

class I2C():
    def __init__(self, bank: int, sda: Pin, scl: Pin):
        pass

    def readfrom(self, address: int, byte_count: int):
        pass

    def writeto(self, address: int, data: bytearray):
        pass

    def scan(self):
        pass
