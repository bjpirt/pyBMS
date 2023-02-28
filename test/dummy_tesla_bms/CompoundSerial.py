class CompoundSerial:
    def __init__(self, txPort, rxPort) -> None:
        self.__txPort = txPort
        self.__rxPort = rxPort

    def read(self):
        return self.__rxPort.read()

    def write(self, value):
        return self.__txPort.write(value)
