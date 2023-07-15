#!/usr/bin/env python3
import time
from battery import crc8
from battery.tesla_model_s.tesla_model_s_constants import BROADCAST_ADDRESS, \
    REG_ADDRESS_CONTROL, REG_DEVICE_STATUS, REG_GPAI, REG_RESET, REG_VCELL1, RESET_VALUE
from hal.interval import get_interval


class TeslaBmsEmulator:

    def __init__(self, serial, name="teslaBmsEmulator", debug_comms: bool = False, debug_interval: float = 0):
        self.__serial = serial
        self.__debug_comms = debug_comms
        self.__debug_interval = debug_interval
        self.__interval = get_interval()
        self.__interval.set(self.__debug_interval)
        self.__receive_timeout = get_interval()
        self.name = name
        self.registers = [0 for _ in range(REG_RESET+1)]
        self.registers[0x0F] = 0x11
        self.registers[0x10] = 0x16
        self.registers[0x11] = 0x11
        self.registers[0x12] = 0x16
        self.buff: bytearray = bytearray()
        for index, voltage in enumerate([3.8, 3.9, 4.0, 4.1, 4.2, 4.3]):
            self.set_cell_voltage(index, voltage)
        self.set_module_voltage(20.295)

    @property
    def address(self):
        return self.registers[REG_ADDRESS_CONTROL] & 0b00111111

    @address.setter
    def address(self, addr: int):
        self.registers[REG_ADDRESS_CONTROL] = addr

    def set_cell_voltage(self, cell_id: int, voltage: float):
        temp: int = int(round(voltage * 16383 / 6.25))
        self.registers[REG_VCELL1 + cell_id * 2] = temp >> 8
        self.registers[REG_VCELL1 + cell_id * 2 + 1] = temp & 0xFF

    def get_cell_voltage(self, cell_id: int) -> float:
        reg = REG_VCELL1 + cell_id * 2
        raw_temp = (self.registers[reg] << 8) + self.registers[reg + 1]
        return round((raw_temp) * 6.25 / 16383, 3)

    def set_module_voltage(self, voltage: float):
        temp: int = int(round(voltage * 49149.0 / 100))
        self.registers[REG_GPAI] = temp >> 8
        self.registers[REG_GPAI + 1] = temp & 0xFF

    def process(self):
        data = self.__serial.read()
        if data and data != '':
            for char in data:
                self.buff.append(char)
            self.__receive_timeout.set(0.1)
        elif self.__receive_timeout.ready:
            self.buff = bytearray()

        if len(self.buff) >= 4:
            incoming = bytearray([i for i in self.buff[0:-1]])
            incoming[0] = incoming[0] & 0b01111111
            if crc8(incoming) != self.buff[-1]:
                return
            if self.__debug_comms:
                print(f"Received by device {self.name} address {self.address}", [
                    hex(char) for char in self.buff])
            msg_address = self.buff[0] >> 1
            if msg_address in (self.address, BROADCAST_ADDRESS):
                if crc8(self.buff[0:-1]) == self.buff[-1]:
                    self.__handle_message()
            else:
                if self.__debug_comms:
                    print("Forwarding")
                self.__serial.write(self.buff)
            self.buff = bytearray()
        self.__print_debug()

    def __print_debug(self):
        if self.__debug_interval > 0 and self.__interval.ready:
            voltages = [self.get_cell_voltage(i) for i in range(6)]
            print(f"Voltage: {sum(voltages)} time: {time.time()}")
            for cell_id, voltage in enumerate(voltages):
                print(f"  |- Cell: {cell_id} voltage: {voltage}")
            self.__interval.set(self.__debug_interval)

    def __handle_message(self):
        current_address = self.address
        msg_address = self.buff[0] >> 1
        msg_write = bool(self.buff[0] & 1)
        register = self.buff[1]
        response: bytearray = bytearray(list(self.buff[0:-1]))
        if msg_write:
            if self.__debug_comms:
                print(
                    f"Setting register {hex(register)} to {hex(self.buff[2])}")
            if register == REG_RESET and self.buff[2] == RESET_VALUE:
                if self.__debug_comms:
                    print(f"Resetting address from {self.address} to 0")
                self.address = 0
            elif register == REG_ADDRESS_CONTROL:
                new_address = self.buff[2] & 0b00111111
                if self.__debug_comms:
                    print(f"Setting address to {new_address}")
                self.registers[register] = new_address | 0x80
                self.registers[REG_DEVICE_STATUS] = 0x08
            else:
                self.registers[register] = self.buff[2]
        else:
            if self.__debug_comms:
                print(
                    f"Reading {hex(self.buff[2])} registers from {hex(register)}")
            for i in range(self.buff[2]):
                response.append(self.registers[self.buff[1] + i] & 0xFF)
        response.append(crc8(response))
        if msg_address == 0 and current_address == 0:
            response[0] = self.buff[0] | 0x80
        if self.__debug_comms:
            print(f"Sending response from {self.name}", [
                  hex(c) for c in response])
        self.__serial.write(response)
