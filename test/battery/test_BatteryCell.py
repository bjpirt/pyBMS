from battery import BatteryCell
import unittest


class BatteryCellTestCase(unittest.TestCase):
    def setUp(self):
        self.cell = BatteryCell()

    def test_store_highest_voltage(self):
        self.cell.voltage = 3.0
        self.assertEqual(self.cell.voltage, 3.0)
        self.assertEqual(self.cell.highestVoltage, 3.0)
        self.cell.voltage = 2.9
        self.assertEqual(self.cell.voltage, 2.9)
        self.assertEqual(self.cell.highestVoltage, 3.0)
        self.cell.voltage = 3.1
        self.assertEqual(self.cell.voltage, 3.1)
        self.assertEqual(self.cell.highestVoltage, 3.1)

    def test_store_lowest_voltage(self):
        self.cell.voltage = 3.0
        self.assertEqual(self.cell.voltage, 3.0)
        self.assertEqual(self.cell.lowestVoltage, 3.0)
        self.cell.voltage = 2.9
        self.assertEqual(self.cell.voltage, 2.9)
        self.assertEqual(self.cell.lowestVoltage, 2.9)
        self.cell.voltage = 3.1
        self.assertEqual(self.cell.voltage, 3.1)
        self.assertEqual(self.cell.lowestVoltage, 2.9)

    def test_has_fault(self):
        self.cell.voltage = 4.0
        self.assertFalse(self.cell.hasFault)
        self.cell.voltage = 3.0
        self.assertTrue(self.cell.hasFault)
        self.cell.voltage = 5.0
        self.assertTrue(self.cell.hasFault)
