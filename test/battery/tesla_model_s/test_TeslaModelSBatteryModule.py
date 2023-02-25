from typing import List, Union
import unittest
from unittest.mock import MagicMock

from battery.tesla_model_s.TeslaModelSBatteryModule import TeslaModelSBatteryModule
from battery.tesla_model_s.TeslaModelSNetworkGateway import TeslaModelSNetworkGateway


class FakeGateway(TeslaModelSNetworkGateway):
    def readRegister(self, address: int, register: int, length: int) -> Union[List[int], None]:
        return None

    def writeRegister(self, address: int, register: int, value: int) -> bool:
        return True


mockValidRead = [
    0x00, 0x20, 0x00, 0x26, 0xF7, 0x26, 0xF7, 0x26, 0xF7, 0x26,
    0xF7, 0x26, 0xF7, 0x26, 0xF7, 0x11, 0x16, 0x11, 0x16
]

mockInvalidRead = [
    0x60, 0x20, 0x00, 0x26, 0xF7, 0x26, 0xF7, 0x26, 0xF7, 0x26,
    0xF7, 0x26, 0xF7, 0x26, 0xF7, 0x11, 0x16, 0x11, 0x16
]

mockStatusRead = [0x03, 0x03, 0x07, 0x38]


class TeslaModelSBatteryModuleTestCase(unittest.TestCase):

    def setUp(self):
        self.mockGateway = FakeGateway(None)
        self.mockGateway.writeRegister = MagicMock(return_value=True)
        self.module = TeslaModelSBatteryModule(1, self.mockGateway)
        return super().setUp()

    def test_update(self):
        self.mockGateway.readRegister = MagicMock(return_value=mockValidRead)
        self.module.update()
        self.assertEqual(self.module.voltage, 1.25)
        for cell in self.module.cells:
            self.assertEqual(cell.voltage, 20.295)
            self.assertFalse(cell.underVoltageFault)
            self.assertFalse(cell.overVoltageFault)
        self.assertFalse(self.module.alert)
        self.assertFalse(self.module.fault)
        self.assertEqual(self.module.temperatures[0], 25.343)
        self.assertEqual(self.module.temperatures[1], 25.343)

    def test_update_bad_status(self):
        self.mockGateway.readRegister = MagicMock()
        self.mockGateway.readRegister.side_effect = [
            mockInvalidRead, mockStatusRead]
        self.module.update()
        self.assertTrue(self.module.alert)
        self.assertTrue(self.module.fault)
        for cell in self.module.cells[0:3]:
            self.assertTrue(cell.overVoltageFault)
            self.assertFalse(cell.underVoltageFault)
        for cell in self.module.cells[3:6]:
            self.assertFalse(cell.overVoltageFault)
            self.assertTrue(cell.underVoltageFault)
