class TeslaModelSNetworkGateway:
    def __init__(self, serial):
        self.__serial = serial

    def readRegister(self, address: int, register: int, length: int):
        pass

    def writeRegister(self, address: int, register: int, value: int):
        pass
