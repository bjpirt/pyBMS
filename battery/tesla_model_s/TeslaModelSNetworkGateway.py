import time
from typing import List, Union

from battery.tesla_model_s.crc8 import crc8


class TeslaModelSNetworkGateway:
    def __init__(self, serial, debug=False):
        self.__serial = serial
        self.debug = debug
        self.receiveBuffer: bytearray = bytearray()

    def readRegister(self, address: int, register: int, length: int) -> Union[bytearray, None]:
        message = bytearray(
            [(address << 1) & 0xFF, register & 0xFF, length & 0xFF])
        message.append(crc8(message))
        if self.debug:
            print("Sending read in gateway", [hex(c) for c in message])
        self.__serial.write(message)
        response = self.__receiveResponse()
        if response:
            if self.debug:
                print("Read response in gateway", [hex(c) for c in response])
            return response[3:-1]

    def writeRegister(self, address: int, register: int, value: int) -> bool:
        message = bytearray(
            [((address << 1) & 0xFF) | 0x01, register & 0xFF, value & 0xFF])
        message.append(crc8(message))
        if self.debug:
            print("Sending write in gateway", [hex(c) for c in message])
        self.__serial.write(message)
        # TODO: Check the response message matches the write message
        # TODO: Validate the checksum
        response = self.__receiveResponse()
        if response:
            if self.debug:
                print("Write response in gateway", [hex(c) for c in response])
            return True
        return False

    def _expectedMessageLength(self) -> int:
        if len(self.receiveBuffer) >= 3:
            msgWrite = bool(self.receiveBuffer[0] & 1)
            if msgWrite:
                return 4
            forwarded = self.receiveBuffer[0] & 0x80 > 0
            if forwarded:
                return self.receiveBuffer[2] + 4
        return 4

    def __receiveResponse(self):
        timeoutTime = time.time() + 5
        while time.time() < timeoutTime:
            readData = self.__serial.read()
            for c in readData:
                self.receiveBuffer.append(c)
            if len(self.receiveBuffer) >= self._expectedMessageLength():
                result = self.receiveBuffer[0:self._expectedMessageLength()]
                self.receiveBuffer = bytearray(
                    self.receiveBuffer[self._expectedMessageLength():])
                return result
        return None
