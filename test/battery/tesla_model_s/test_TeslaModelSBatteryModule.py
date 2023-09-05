from typing import Union
import unittest
from unittest.mock import MagicMock, call

from battery.tesla_model_s.tesla_model_s_battery_module import TeslaModelSBatteryModule
from battery.tesla_model_s.tesla_model_s_constants import REG_CB_CTRL, REG_CB_TIME
from battery.tesla_model_s.tesla_model_s_network_gateway import TeslaModelSNetworkGateway
from config import Config


class FakeGateway(TeslaModelSNetworkGateway):
    def read_register(self, address: int, register: int, length: int, attempts: int = 5) -> Union[bytearray, None]:
        return None

    def write_register(self, address: int, register: int, value: int, attempts: int = 5) -> bool:
        return True


mockValidRead = [
    0x00, 0x26, 0xF7, 0x22, 0x4D, 0x22, 0x4D, 0x22, 0x4D, 0x22,
    0x4D, 0x22, 0x4D, 0x22, 0x4D, 0x11, 0x16, 0x11, 0x16
]

mockInvalidRead = [
    0x60, 0x26, 0xF7, 0x22, 0x4D, 0x22, 0x4D, 0x22, 0x4D, 0x22,
    0x4D, 0x22, 0x4D, 0x22, 0x4D, 0x11, 0x16, 0x11, 0x16
]

mockStatusRead = [0x03, 0x03, 0x07, 0x38]


class TeslaModelSBatteryModuleTestCase(unittest.TestCase):

    def setUp(self):
        c = Config("config.default.json")
        c.balance_hysteresis_time = 0
        self.mockGateway = FakeGateway(None, Config("config.default.json"))
        self.mockGateway.write_register = MagicMock(return_value=True)
        self.module = TeslaModelSBatteryModule(1, self.mockGateway, c)
        return super().setUp()

    def test_update(self):
        self.mockGateway.read_register = MagicMock(return_value=mockValidRead)
        self.module.update()
        self.assertEqual(self.module.voltage, 20.295)
        for cell in self.module.cells:
            self.assertEqual(cell.voltage, 3.35)
        self.assertEqual(self.module.temperatures[0], 25.343)
        self.assertEqual(self.module.temperatures[1], 25.343)

    def test_update_bad_status(self):
        self.mockGateway.read_register = MagicMock()
        self.mockGateway.read_register.side_effect = [
            mockInvalidRead, mockStatusRead]
        self.module.update()
        self.assertTrue(self.module.alert)
        self.assertTrue(self.module.fault)

    def test_balance(self):
        self.mockGateway.write_register = MagicMock(return_value=True)
        for cell in self.module.cells:
            cell.balancing = False
        self.module.cells[1].balancing = True
        self.module.cells[3].balancing = True
        self.module.balance()

        self.mockGateway.write_register.assert_has_calls(
            [call(self.module.address, REG_CB_TIME, 5), call(self.module.address,
                                                             REG_CB_CTRL, 0b00001010)])
