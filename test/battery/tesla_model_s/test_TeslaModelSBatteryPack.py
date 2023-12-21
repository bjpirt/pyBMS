from typing import Union
import unittest
from unittest.mock import MagicMock

from battery.tesla_model_s.tesla_model_s_battery_pack import TeslaModelSBatteryPack
from battery.tesla_model_s.tesla_model_s_network_gateway import TeslaModelSNetworkGateway
from config import Config


class FakeGateway(TeslaModelSNetworkGateway):
    def read_register(self, address: int, register: int, length: int, attempts: int = 5) -> Union[bytearray, None]:
        return None

    def write_register(self, address: int, register: int, value: int, attempts: int = 5) -> bool:
        return True


mockDeviceStatusRead = [0x00]
mockDeviceAddressRead1 = [0x81]
mockDeviceAddressRead2 = [0x82]
mockValidRead = [
    0x00, 0x28, 0xF7, 0x28, 0x5E, 0x22, 0x4D, 0x22, 0x4D, 0x22,
    0x4D, 0x22, 0x4D, 0x22, 0x4D, 0x11, 0x16, 0x11, 0x16
]


class TeslaModelSBatteryPackTestCase(unittest.TestCase):

    def setUp(self):
        self.mockGateway = FakeGateway(None, Config())
        self.mockGateway.write_register = MagicMock(return_value=True)
        self.config = Config()
        self.config.module_count = 2
        return super().setUp()

    def test_setup_modules(self):
        self.mockGateway.read_register = MagicMock()
        self.mockGateway.read_register.side_effect = [
            mockDeviceStatusRead, mockDeviceAddressRead1, mockValidRead,
            mockDeviceStatusRead, mockDeviceAddressRead2, mockValidRead, None]
        self.pack = TeslaModelSBatteryPack(self.mockGateway, self.config)
        self.assertEqual(len(self.pack.modules), 2)
        self.assertEqual(self.pack.modules[0].address, 1)
        self.assertEqual(self.pack.modules[1].address, 2)
