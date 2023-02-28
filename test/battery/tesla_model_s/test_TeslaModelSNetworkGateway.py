import unittest
from unittest.mock import MagicMock

from battery.tesla_model_s.TeslaModelSNetworkGateway import TeslaModelSNetworkGateway


class FakeSerial:
    def read(self, length):
        pass

    def write(self, message):
        pass


class TeslaModelSNetworkGatewayTestCase(unittest.TestCase):

    def setUp(self):
        self.serial = FakeSerial()
        self.serial.write = MagicMock()
        self.gateway = TeslaModelSNetworkGateway(self.serial)
        return super().setUp()

    def test_write_register(self):
        self.serial.read = MagicMock(return_value=[0x89, 10, 11, 0xFF])
        result = self.gateway.writeRegister(9, 10, 11)
        self.assertTrue(result)
        self.serial.write.assert_called_with(bytearray([19, 10, 11, 172]))

    def test_read_register(self):
        self.serial.read = MagicMock(
            return_value=bytearray([0x89, 10, 4, 1, 2, 3, 4, 0xFF]))
        result = self.gateway.readRegister(9, 10, 4)
        self.assertEqual(result, bytearray([1, 2, 3, 4]))
        self.serial.write.assert_called_with(bytearray([18, 10, 4, 234]))
