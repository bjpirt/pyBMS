import unittest

from emulator.tesla_bms import TeslaBmsEmulator


class FakeSerial:
    def read(self, length):
        pass

    def write(self, message):
        pass


class TeslaBmsEmulatorTestCase(unittest.TestCase):
    def setUp(self):
        self.emulator = TeslaBmsEmulator(FakeSerial())

    def test_set_module_voltage(self):
        self.emulator.setCellVoltage(0, 4.25)
        self.assertEqual(self.emulator.getCellVoltage(0), 4.25)
