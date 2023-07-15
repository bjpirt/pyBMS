import unittest
from battery.tesla_model_s import crc8
from battery.tesla_model_s.tesla_model_s_constants import (
    BROADCAST_ADDRESS, REG_ADDRESS_CONTROL, REG_CB_CTRL, REG_RESET, RESET_VALUE)
from emulator.tesla_bms import TeslaBmsEmulator
from unittest.mock import MagicMock


def add_crc(message):
    message_copy = bytearray([x for x in message])
    message_copy[0] = message_copy[0] & 0b01111111
    message.append(crc8(message_copy))
    return message


reset_message = add_crc(
    bytearray([BROADCAST_ADDRESS << 1 | 0x01, REG_RESET, RESET_VALUE]))
set_address_message = add_crc(
    bytearray([0x01, REG_ADDRESS_CONTROL, 1]))
set_address_response = add_crc(
    bytearray([0x81, REG_ADDRESS_CONTROL, 1]))
write_balance_control = add_crc(
    bytearray([1 << 1 | 0x01, REG_CB_CTRL, 0x33]))
read_balance_control = add_crc(
    bytearray([0x01 << 1, REG_CB_CTRL, 1]))
read_balance_control_response = add_crc(
    bytearray([0x01 << 1, REG_CB_CTRL, 1, 0x44]))


class FakeSerial:
    def read(self, length):
        pass

    def write(self, message):
        pass


class TeslaBmsEmulatorTestCase(unittest.TestCase):
    def setUp(self):
        self.serial = FakeSerial()
        self.serial.read = MagicMock()
        self.serial.write = MagicMock()
        self.emulator = TeslaBmsEmulator(self.serial)

    def test_set_module_voltage(self):
        self.emulator.set_cell_voltage(0, 4.25)
        self.assertEqual(self.emulator.get_cell_voltage(0), 4.25)

    def test_reset_address(self):
        self.emulator.address = 1
        self.serial.read.side_effect = [reset_message]
        self.emulator.process()
        self.assertEqual(self.emulator.address, 0)
        self.serial.write.assert_called_once_with(reset_message)

    def test_set_address(self):
        self.emulator.address = 0
        self.serial.read.side_effect = [set_address_message]
        self.emulator.process()
        self.assertEqual(self.emulator.address, 0x01)
        self.serial.write.assert_called_once_with(set_address_response)

    def test_write_register_for_self(self):
        self.emulator.address = 1
        self.emulator.registers[REG_CB_CTRL] = 0
        self.serial.read.side_effect = [write_balance_control]
        self.emulator.process()
        self.assertEqual(self.emulator.registers[REG_CB_CTRL], 0x33)
        self.serial.write.assert_called_once_with(write_balance_control)

    def test_write_register_for_other_device(self):
        self.emulator.address = 2
        self.emulator.registers[REG_CB_CTRL] = 0
        self.serial.read.side_effect = [write_balance_control]
        self.emulator.process()
        self.assertEqual(self.emulator.registers[REG_CB_CTRL], 0)
        self.serial.write.assert_called_once_with(write_balance_control)

    def test_read_register_for_self(self):
        self.emulator.address = 1
        self.emulator.registers[REG_CB_CTRL] = 0x44
        self.serial.read.side_effect = [read_balance_control]
        self.emulator.process()
        self.serial.write.assert_called_once_with(
            read_balance_control_response)

    def test_read_register_for_other_device(self):
        self.emulator.address = 2
        self.emulator.registers[REG_CB_CTRL] = 0x44
        self.serial.read.side_effect = [read_balance_control]
        self.emulator.process()
        self.serial.write.assert_called_once_with(
            read_balance_control)

    def test_forward_read_register_result_from_other_device(self):
        self.emulator.address = 2
        self.emulator.registers[REG_CB_CTRL] = 0x44
        self.serial.read.side_effect = [read_balance_control_response]
        self.emulator.process()
        self.serial.write.assert_called_once_with(
            read_balance_control_response)
