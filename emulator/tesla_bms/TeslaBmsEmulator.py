#!/usr/bin/env python3
import time
from battery import crc8

from battery.tesla_model_s.TeslaModelSConstants import *
from hal.interval import get_interval

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

    def __init__(self, serial, name="teslaBmsEmulator", debugComms: bool = False, debugInterval: float = 0):
        self.__serial = serial
        self.__debugComms = debugComms
        self.__debugInterval = debugInterval
        self.__interval = get_interval()
        self.__interval.set(self.__debugInterval)
        self.__receiveTimeout = get_interval()
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
        return self.registers[REG_ADDRESS_CONTROL] & 0b00111111

    @address.setter
    def address(self, addr: int):
        self.registers[REG_ADDRESS_CONTROL] = addr

    def setCellVoltage(self, cellId: int, voltage: float):
        temp: int = int(round(voltage * 16383 / 6.25))
        self.registers[REG_VCELL1 + cellId * 2] = temp >> 8
        self.registers[REG_VCELL1 + cellId * 2 + 1] = temp & 0xFF

    def getCellVoltage(self, cellId: int) -> float:
        reg = REG_VCELL1 + cellId * 2
        rawTemp = (self.registers[reg] << 8) + self.registers[reg + 1]
        return round((rawTemp) * 6.25 / 16383, 3)

    def setModuleVoltage(self, voltage: float):
        temp: int = int(round(voltage * 49149.0 / 100))
        self.registers[REG_GPAI] = temp >> 8
        self.registers[REG_GPAI + 1] = temp & 0xFF

    def process(self):
        input = self.__serial.read()
        if input and input != '':
            for c in input:
                self.buff.append(c)
            self.__receiveTimeout.set(0.1)
        elif self.__receiveTimeout.ready:
            self.buff = bytearray()

        if len(self.buff) >= 4 and crc8(self.buff[0:-1]) == self.buff[-1]:
            if self.__debugComms:
                print(f"Received by device {self.name} address {self.address}", [
                    hex(c) for c in self.buff])
            msgAddress = self.buff[0] >> 1
            if msgAddress == self.address or msgAddress == BROADCAST_ADDRESS:
                if crc8(self.buff[0:-1]) == self.buff[-1]:
                    self.__handleMessage()
            else:
                if self.__debugComms:
                    print("Forwarding")
                self.__serial.write(self.buff)
            self.buff = bytearray()
        self.__printDebug()

    def __printDebug(self):
        if self.__debugInterval > 0 and self.__interval.ready:
            voltages = [self.getCellVoltage(i) for i in range(6)]
            print(f"Voltage: {sum(voltages)} time: {time.time()}")
            for i, v in enumerate(voltages):
                print(f"  |- Cell: {i} voltage: {v}")
            self.__interval.set(self.__debugInterval)

    def __handleMessage(self):
        msgAddress = self.buff[0] >> 1
        msgWrite = bool(self.buff[0] & 1)
        register = self.buff[1]
        response: bytearray = bytearray([c for c in self.buff[0:-1]])
        if msgAddress == 0 and self.address == 0:
            response[0] = self.buff[0] | 0x80
        if msgWrite:
            if self.__debugComms:
                print(
                    f"Setting register {hex(register)} to {hex(self.buff[2])}")
            if register == REG_RESET and self.buff[2] == RESET_VALUE:
                if self.__debugComms:
                    print(f"Resetting address from {self.address} to 0")
                self.address = 0
            elif register == REG_ADDRESS_CONTROL:
                newAddress = self.buff[2] & 0b00111111
                if self.__debugComms:
                    print(f"Setting address to {newAddress}")
                self.registers[register] = newAddress | 0x80
                self.registers[REG_DEVICE_STATUS] = 0x08
            else:
                self.registers[register] = self.buff[2]
        else:
            if self.__debugComms:
                print(
                    f"Reading {hex(self.buff[2])} registers from {hex(register)}")
            for i in range(self.buff[2]):
                response.append(self.registers[self.buff[1] + i] & 0xFF)
        response.append(crc8(response))
        if self.__debugComms:
            print(f"Sending response from {self.name}", [
                  hex(c) for c in response])
        self.__serial.write(response)
