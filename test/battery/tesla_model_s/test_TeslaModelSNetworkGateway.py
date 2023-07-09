import unittest
from unittest.mock import MagicMock

from battery.tesla_model_s.tesla_model_s_network_gateway import TeslaModelSNetworkGateway
from bms import Config


class FakeSerial:
    def read(self, length):
        pass

    def write(self, message):
        pass


class TeslaModelSNetworkGatewayTestCase(unittest.TestCase):

    def setUp(self):
        self.serial = FakeSerial()
        self.serial.write = MagicMock()
        self.gateway = TeslaModelSNetworkGateway(
            self.serial, Config("config.default.json"))
        return super().setUp()

    def test_write_register(self):
        self.serial.read = MagicMock(return_value=[0x92, 10, 11, 0xC7])
        result = self.gateway.write_register(9, 10, 11)
        self.assertTrue(result)
        self.serial.write.assert_called_with(bytearray([19, 10, 11, 172]))

    def test_read_register(self):
        self.serial.read = MagicMock(
            return_value=[0x92, 10, 4, 1, 2, 3, 4, 0x1B])
        result = self.gateway.read_register(9, 10, 4)
        self.assertEqual(result, bytearray([1, 2, 3, 4]))
        self.serial.write.assert_called_with(bytearray([18, 10, 4, 234]))
