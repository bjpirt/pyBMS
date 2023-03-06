#!/usr/bin/env python3
from battery import crc8

from battery.tesla_model_s.TeslaModelSConstants import *

"""
Message format:
 Byte 0 LSB: 1 = write 0 = read
 Byte 0 bits 1 - 7 = address
 Byte 1 = register
 Byte 2 = length / value
 Byte 3 = checksum

| Address     | Register |
--------------------------
| 0x00        | Device Status |
| 0x01 - 0x02 | Module voltage |
| 0x03 - 0x04 | Cell 1 voltage |
| 0x05 - 0x06 | Cell 2 voltage |
| 0x07 - 0x08 | Cell 3 voltage |
| 0x09 - 0x0A | Cell 4 voltage |
| 0x0B - 0x0C | Cell 5 voltage |
| 0x0D - 0x0E | Cell 6 voltage |
| 0x0F - 0x10 | Temperature 1 |
| 0x11 - 0x12 | Temperature 2 |
| 0x20        | Alerts |
| 0x21        | Faults |
| 0x22        | Over-Voltage faults |
| 0x23        | Under-Voltage faults |
| 0x31        | I/O control |
| 0x32        | Balance control |
| 0x33        | Balance time |
| 0x34        | ADC Control |
| 0x3B        | Network Address |
"""


class TeslaBmsEmulator:

    def __init__(self, serial, name="teslaBmsEmulator", debug=False):
        self.__serial = serial
        self.debug = debug
        self.name = name
        self.registers = [0 for _ in range(REG_RESET+1)]
        self.registers[0x0F] = 0x11
        self.registers[0x10] = 0x16
        self.registers[0x11] = 0x11
        self.registers[0x12] = 0x16
        self.buff: bytearray = bytearray()
        for i, v in enumerate([3.8, 3.9, 4.0, 4.1, 4.2, 4.3]):
            self.setCellVoltage(i, v)
        self.setModuleVoltage(20.295)

    @property
    def address(self):
        return self.registers[REG_ADDRESS_CONTROL]

    @address.setter
    def address(self, addr: int):
        self.registers[REG_ADDRESS_CONTROL] = addr

    def setCellVoltage(self, cellId: int, voltage: float):
        temp: int = int(round(voltage * 16383 / 6.25))
        self.registers[REG_VCELL1 + cellId * 2] = temp >> 8
        self.registers[REG_VCELL1 + cellId * 2 + 1] = temp & 0xFF

    def setModuleVoltage(self, voltage: float):
        temp: int = int(round(voltage * 49149.0 / 100))
        self.registers[REG_GPAI] = temp >> 8
        self.registers[REG_GPAI + 1] = temp & 0xFF

    def _expectedMessageLength(self) -> int:
        if len(self.buff) >= 3:
            msgWrite = bool(self.buff[0] & 1)
            if msgWrite:
                return 4
            forwarded = self.buff[0] & 0x80 > 0
            if forwarded:
                return self.buff[2] + 4
        return 4

    def process(self):
        input = self.__serial.read()
        if input and input != '':
            for c in input:
                self.buff.append(c)

        if len(self.buff) >= self._expectedMessageLength():
            if self.debug:
                print(f"Received by device {self.name}", [
                    hex(c) for c in self.buff])
            msgAddress = self.buff[0] >> 1
            if msgAddress == self.address or msgAddress == BROADCAST_ADDRESS:
                if crc8(self.buff[0:3]) == self.buff[3]:
                    self.handleMessage()
            else:
                if self.debug:
                    print("Forwarding")
                self.__serial.write(self.buff)
            self.buff = self.buff[self._expectedMessageLength():]

    def handleMessage(self):
        msgAddress = self.buff[0] >> 1
        msgWrite = bool(self.buff[0] & 1)
        register = self.buff[1]
        response: bytearray = bytearray([c for c in self.buff[0:-1]])
        if msgAddress != BROADCAST_ADDRESS:
            response[0] = self.buff[0] | 0x80
        if msgWrite:
            if self.debug:
                print(
                    f"Setting register {hex(register)} to {hex(self.buff[2])}")
            if register == REG_RESET and self.buff[2] == RESET_VALUE:
                if self.debug:
                    print(f"Resetting address from {self.address} to 0")
                self.address = 0
            elif register == REG_ADDRESS_CONTROL:
                newAddress = self.buff[2] & 0b01111111
                if self.debug:
                    print(f"Setting address to {newAddress}")
                self.registers[register] = newAddress
                self.registers[REG_DEVICE_STATUS] = 0x08
            else:
                self.registers[register] = self.buff[2]
        else:
            if self.debug:
                print(
                    f"Reading {hex(self.buff[2])} registers from {hex(register)}")
            for i in range(self.buff[2]):
                response.append(self.registers[self.buff[1] + i] & 0xFF)
        response.append(crc8(response))
        if self.debug:
            print(f"Sending response from {self.name}", [
                  hex(c) for c in response])
        self.__serial.write(response)
