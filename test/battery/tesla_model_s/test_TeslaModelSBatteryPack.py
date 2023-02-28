from typing import List, Union
import unittest
from unittest.mock import MagicMock, call

from battery.tesla_model_s.TeslaModelSBatteryPack import TeslaModelSBatteryPack
from battery.tesla_model_s.TeslaModelSConstants import REG_CB_CTRL, REG_CB_TIME
from battery.tesla_model_s.TeslaModelSNetworkGateway import TeslaModelSNetworkGateway


class FakeGateway(TeslaModelSNetworkGateway):
    def readRegister(self, address: int, register: int, length: int) -> Union[List[int], None]:
        return None

    def writeRegister(self, address: int, register: int, value: int) -> bool:
        return True


mockDeviceStatusRead = [0x00]
mockDeviceStatusRead2 = [0xFF]
mockValidRead = [
    0x00, 0x26, 0xF7, 0x22, 0x5E, 0x22, 0x4D, 0x22, 0x4D, 0x22,
    0x4D, 0x22, 0x4D, 0x22, 0x4D, 0x11, 0x16, 0x11, 0x16
]


class TeslaModelSBatteryPackTestCase(unittest.TestCase):

    def setUp(self):
        self.mockGateway = FakeGateway(None)
        self.mockGateway.writeRegister = MagicMock(return_value=True)
        return super().setUp()

    def test_setup_modules(self):
        self.mockGateway.readRegister = MagicMock()
        self.mockGateway.readRegister.side_effect = [
            mockDeviceStatusRead, mockDeviceStatusRead2, mockDeviceStatusRead, mockDeviceStatusRead2, None]
        self.pack = TeslaModelSBatteryPack(2, self.mockGateway)
        self.assertEqual(len(self.pack.modules), 2)
        self.assertEqual(self.pack.modules[0].address, 1)
        self.assertEqual(self.pack.modules[1].address, 2)

    def test_balance(self):
        self.mockGateway.readRegister = MagicMock()
        self.mockGateway.readRegister.side_effect = [
            mockDeviceStatusRead, mockDeviceStatusRead2, mockDeviceStatusRead, mockDeviceStatusRead2, None,
            mockValidRead, mockValidRead]
        self.pack = TeslaModelSBatteryPack(2, self.mockGateway)
        self.assertEqual(len(self.pack.modules), 2)
        self.pack.update()

        self.mockGateway.writeRegister.assert_any_call(
            self.pack.modules[0].address, REG_CB_TIME, 5)
        self.mockGateway.writeRegister.assert_any_call(
            self.pack.modules[0].address, REG_CB_CTRL, 0b00000001)
        self.mockGateway.writeRegister.assert_any_call(
            self.pack.modules[1].address, REG_CB_TIME, 5)
        self.mockGateway.writeRegister.assert_any_call(
            self.pack.modules[1].address, REG_CB_CTRL, 0b00000001)
