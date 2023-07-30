from __future__ import annotations
from typing import TYPE_CHECKING
from hal.interval import get_interval
from .crc8 import crc8
if TYPE_CHECKING:
    from typing import Union
    from bms import Config


class TeslaModelSNetworkGateway:
    def __init__(self, serial, config: Config):
        self.__serial = serial
        self.__config = config
        self.receive_buffer: bytearray = bytearray()

    def read_register(self, address: int, register: int, length: int, attempts: int = 5) -> Union[bytearray, None]:
        message = bytearray(
            [(address << 1) & 0xFF, register & 0xFF, length & 0xFF])
        message.append(crc8(message))

        if self.__config.debugComms:
            print("Sending register read", [hex(c) for c in message])

        self.__serial.write(message)

        response = self.__receive_response(4 + length)
        if response:
            if (response[0] >> 1) == address and response[1] == register and response[2] == length:
                if self.__config.debugComms:
                    print("Received response", [hex(c) for c in response])

                return response[3:-1]

        if attempts > 0:
            return self.read_register(address, register, length, attempts - 1)

        return None

    def write_register(self, address: int, register: int, value: int, attempts: int = 5) -> bool:
        message = bytearray(
            [((address << 1) & 0xFF) | 0x01, register & 0xFF, value & 0xFF])
        message.append(crc8(message))

        if self.__config.debugComms:
            print("Sending register write", [hex(c) for c in message])

        self.__serial.write(message)

        response = self.__receive_response(4)
        if response:
            if self.__config.debugComms:
                print("Received response", [hex(c) for c in response])

            if (response[0] >> 1) == address and response[1] == register and response[2] == value:
                return True

        if attempts > 0:
            return self.write_register(address, register, value, attempts - 1)

        self.receive_buffer = bytearray()
        return False

    def __receive_response(self, length):
        interval = get_interval()
        interval.set(0.1)
        while not interval.ready:
            read_data = self.__serial.read()
            if read_data and str(read_data) != '':
                for char in read_data:
                    self.receive_buffer.append(char)
                if len(self.receive_buffer) >= length:
                    result = self.receive_buffer[0:length]
                    self.receive_buffer = bytearray()
                    result[0] = result[0] & 0b01111111
                    if crc8(result[:-1]) == result[-1]:
                        return result
                    else:
                        self.__clear_buffer()
                        return None
        if self.__config.debugComms:
            print("Timed out")
        self.receive_buffer = bytearray()
        return None

    def __clear_buffer(self):
        self.receive_buffer = bytearray()

        interval = get_interval()
        interval.set(0.1)
        while not interval.ready:
            read_data = self.__serial.read(1)
            if not read_data or len(read_data) == 0:
                return
