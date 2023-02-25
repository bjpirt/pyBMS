from typing import List, Union


class TeslaModelSNetworkGateway:
    def __init__(self, serial):
        self.__serial = serial

    def readRegister(self, address: int, register: int, length: int) -> Union[List[int], None]:
        message = bytearray(
            [(address << 1) & 0xFF, register & 0xFF, length & 0xFF])
        message.append(self.__checksum(message))
        self.__serial.write(message)
        response = self.__receiveResponse(length + 4)
        if response:
            return response[2:-1]

    def writeRegister(self, address: int, register: int, value: int) -> bool:
        message = bytearray(
            [((address << 1) & 0xFF) | 0x01, register & 0xFF, value & 0xFF])
        message.append(self.__checksum(message))
        self.__serial.write(message)
        # TODO: Check the response message matches the write message
        # TODO: Validate the checksum
        if self.__receiveResponse(4):
            return True
        return False

    def __receiveResponse(self, length):
        # TODO: Implement receive timeout
        return self.__serial.read(length)

    def __checksum(self, message: bytearray) -> int:
        seed: int = 0x07
        crc: int = 0

        for c in message:
            crc = crc ^ c

            for i in range(8):
                if crc & 0x80 != 0:
                    crc = ((crc << 1) & 0xFF) ^ seed
                else:
                    crc = (crc << 1) & 0xFF

        return crc & 0xFF
