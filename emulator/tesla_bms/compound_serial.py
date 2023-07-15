class CompoundSerial:
    def __init__(self, tx_port, rx_port) -> None:
        self.__tx_port = tx_port
        self.__rx_port = rx_port

    def read(self, length=1):
        return self.__rx_port.read(length)

    def write(self, value):
        return self.__tx_port.write(value)
