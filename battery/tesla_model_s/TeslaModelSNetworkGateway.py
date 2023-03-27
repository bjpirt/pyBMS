import time
from typing import Union
from bms import Config

from hal.interval import get_interval
from . import crc8


class TeslaModelSNetworkGateway:
    def __init__(self, serial, config: Config):
        self.__serial = serial
        self.__config = config
        self.receiveBuffer: bytearray = bytearray()

    def readRegister(self, address: int, register: int, length: int) -> Union[bytearray, None]:
        message = bytearray(
            [(address << 1) & 0xFF, register & 0xFF, length & 0xFF])
        message.append(crc8(message))
        if self.__config.debug:
            print("Sending register read", [hex(c) for c in message])
        self.__serial.write(message)
        response = self.__receiveResponse(4 + length)
        if response:
            if self.__config.debug:
                print("Received response", [hex(c) for c in response])
            return response[3:-1]

    def writeRegister(self, address: int, register: int, value: int) -> bool:
        message = bytearray(
            [((address << 1) & 0xFF) | 0x01, register & 0xFF, value & 0xFF])
        message.append(crc8(message))
        if self.__config.debug:
            print("Sending register write", [hex(c) for c in message])
        self.__serial.write(message)
        # TODO: Check the response message matches the write message
        # TODO: Validate the checksum
        response = self.__receiveResponse(4)
        if response:
            if self.__config.debug:
                print("Received response", [hex(c) for c in response])
            return True
        self.receiveBuffer = bytearray()
        return False

    def __receiveResponse(self, length):
        interval = get_interval()
        interval.set(0.1)
        while not interval.ready:
            readData = self.__serial.read()
            if readData and readData != '':
                for c in readData:
                    self.receiveBuffer.append(c)
                if len(self.receiveBuffer) >= length:
                    result = self.receiveBuffer[0:length]
                    self.receiveBuffer = bytearray()
                    return result
        self.receiveBuffer = bytearray()
        return None
