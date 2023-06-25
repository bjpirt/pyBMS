from battery import BatteryCell
import unittest

from bms import Config


class BatteryCellTestCase(unittest.TestCase):
    def setUp(self):
        c = Config("config.default.json")
        self.cell = BatteryCell(c)

    def test_store_highest_voltage(self):
        self.cell.voltage = 3.0
        self.assertEqual(self.cell.voltage, 3.0)
        self.assertEqual(self.cell.highest_voltage, 3.0)
        self.cell.voltage = 2.9
        self.assertEqual(self.cell.voltage, 2.9)
        self.assertEqual(self.cell.highest_voltage, 3.0)
        self.cell.voltage = 3.1
        self.assertEqual(self.cell.voltage, 3.1)
        self.assertEqual(self.cell.highest_voltage, 3.1)

    def test_store_lowest_voltage(self):
        self.cell.voltage = 3.0
        self.assertEqual(self.cell.voltage, 3.0)
        self.assertEqual(self.cell.lowest_voltage, 3.0)
        self.cell.voltage = 2.9
        self.assertEqual(self.cell.voltage, 2.9)
        self.assertEqual(self.cell.lowest_voltage, 2.9)
        self.cell.voltage = 3.1
        self.assertEqual(self.cell.voltage, 3.1)
        self.assertEqual(self.cell.lowest_voltage, 2.9)

    def test_has_fault(self):
        self.cell.voltage = 4.0
        self.assertFalse(self.cell.has_fault)
        self.cell.voltage = 3.0
        self.assertTrue(self.cell.has_fault)
        self.cell.voltage = 5.0
        self.assertTrue(self.cell.has_fault)
